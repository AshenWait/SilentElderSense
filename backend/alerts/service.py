"""
告警服务 - 处理告警触发逻辑
"""
from datetime import datetime, time
from typing import Optional, List
from auth.models import get_db
from .models import AlertConfig, AlertHistory, AlertLevel


class AlertService:
    """告警服务"""

    # 风险等级对应的默认告警方式
    DEFAULT_METHODS = {
        'HIGH': ['sms', 'email', 'app'],
        'MEDIUM': ['email', 'app'],
        'LOW': ['app']
    }

    # 风险等级对应的告警级别（三级响应）
    RISK_TO_ALERT_LEVEL = {
        'HIGH': AlertLevel.LEVEL_3,    # 高风险 -> 三级响应（紧急通知）
        'MEDIUM': AlertLevel.LEVEL_2,  # 中风险 -> 二级响应（管理端告警）
        'LOW': AlertLevel.LEVEL_1      # 低风险 -> 一级响应（本地提醒）
    }

    # 告警级别描述
    ALERT_LEVEL_DESC = {
        AlertLevel.LEVEL_1: '一级响应（本地提醒）',
        AlertLevel.LEVEL_2: '二级响应（管理端告警）',
        AlertLevel.LEVEL_3: '三级响应（紧急通知）'
    }

    # 事件类型描述（与 risk_engine.py 保持一致）
    EVENT_DESCRIPTIONS = {
        'FALLEN': '跌倒检测',
        'STILLNESS': '长时间静止',
        'NIGHT_ABNORMAL': '夜间异常活动'
    }

    # 风险等级描述
    RISK_DESCRIPTIONS = {
        'HIGH': '高风险',
        'MEDIUM': '中风险',
        'LOW': '低风险'
    }

    def get_config(self, user_id: int) -> Optional[AlertConfig]:
        """获取用户告警配置"""
        db = next(get_db())
        return db.query(AlertConfig).filter_by(user_id=user_id).first()

    def create_or_update_config(self, user_id: int, **kwargs) -> AlertConfig:
        """创建或更新告警配置"""
        db = next(get_db())
        config = db.query(AlertConfig).filter_by(user_id=user_id).first()

        if config:
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        else:
            config = AlertConfig(user_id=user_id, **kwargs)
            db.add(config)

        db.commit()
        db.refresh(config)
        return config

    def should_alert(self, user_id: int, risk_level: str) -> bool:
        """
        判断是否应该发送告警

        考虑因素：
        1. 用户是否配置了该风险等级的告警
        2. 是否在免打扰时段
        3. 高风险是否绕过免打扰
        """
        config = self.get_config(user_id)
        if not config:
            return True  # 无配置则默认告警

        # 检查免打扰时段
        if self._is_quiet_hours(config):
            # 高风险且配置了绕过免打扰
            if risk_level == 'HIGH' and config.bypass_quiet_hours:
                return True
            return False

        return True

    def _is_quiet_hours(self, config: AlertConfig) -> bool:
        """检查当前是否在免打扰时段"""
        now = datetime.now().time()
        start = datetime.strptime(config.quiet_hours_start, '%H:%M').time()
        end = datetime.strptime(config.quiet_hours_end, '%H:%M').time()

        if start < end:
            # 免打扰时段在同一天内
            return start <= now <= end
        else:
            # 免打扰时段跨越午夜
            return now >= start or now <= end

    def get_alert_methods(self, user_id: int, risk_level: str) -> List[str]:
        """获取指定风险等级的告警方式"""
        config = self.get_config(user_id)

        if not config:
            return self.DEFAULT_METHODS.get(risk_level, ['app'])

        methods_field = f'{risk_level.lower()}_alert_methods'
        methods_str = getattr(config, methods_field, '')

        if methods_str:
            return methods_str.split(',')
        return self.DEFAULT_METHODS.get(risk_level, ['app'])

    def trigger_alert(self, user_id: int, event_id: int, event_type: str,
                      risk_level: str, duration: float = 0) -> List[AlertHistory]:
        """
        触发告警

        Args:
            user_id: 用户ID
            event_id: 关联事件ID
            event_type: 事件类型 (FALLEN, STILLNESS, NIGHT_ABNORMAL)
            risk_level: 风险等级 (HIGH, MEDIUM, LOW)
            duration: 持续时长

        Returns:
            创建的告警记录列表
        """
        if not self.should_alert(user_id, risk_level):
            return []

        methods = self.get_alert_methods(user_id, risk_level)
        config = self.get_config(user_id)

        alerts = []
        for method in methods:
            alert = self._create_alert(
                user_id=user_id,
                event_id=event_id,
                alert_type=method,
                event_type=event_type,
                risk_level=risk_level,
                duration=duration,
                config=config
            )
            alerts.append(alert)

        return alerts

    def _create_alert(self, user_id: int, event_id: int, alert_type: str,
                      event_type: str, risk_level: str, duration: float,
                      config: Optional[AlertConfig] = None) -> AlertHistory:
        """创建告警记录"""
        db = next(get_db())

        # 确定告警级别（三级响应）
        alert_level = self.RISK_TO_ALERT_LEVEL.get(risk_level, AlertLevel.LEVEL_1).value

        # 构建告警内容
        event_desc = self.EVENT_DESCRIPTIONS.get(event_type, event_type)
        risk_desc = self.RISK_DESCRIPTIONS.get(risk_level, risk_level)
        level_desc = self.ALERT_LEVEL_DESC.get(AlertLevel(alert_level), '')

        title = f"【{risk_desc}】{event_desc}告警"
        message = f"检测到{event_desc}事件，风险等级：{risk_desc}，响应级别：{level_desc}，持续时长：{duration:.1f}秒。请及时关注。"

        # 获取接收者
        recipient = None
        if config:
            if alert_type == 'sms':
                recipient = config.emergency_phone
            elif alert_type == 'email':
                recipient = config.email

        alert = AlertHistory(
            user_id=user_id,
            event_id=event_id,
            alert_level=alert_level,
            alert_type=alert_type,
            risk_level=risk_level,
            event_type=event_type,
            title=title,
            message=message,
            recipient=recipient
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        # 尝试发送（实际发送逻辑需要对接第三方服务）
        self._send_alert(alert)

        return alert

    def _send_alert(self, alert: AlertHistory):
        """
        发送告警（三级响应）

        一级响应（本地提醒）：仅记录，不发送外部通知
        二级响应（管理端告警）：推送至管理端高亮显示
        三级响应（紧急通知）：触发短信、电话等紧急通知流程
        """
        db = next(get_db())

        try:
            if alert.alert_level == 1:
                # 一级响应：本地提醒，仅记录
                alert.status = 'sent'
                alert.sent_at = datetime.now()

            elif alert.alert_level == 2:
                # 二级响应：管理端告警
                # TODO: 推送至管理端 WebSocket
                alert.status = 'sent'
                alert.sent_at = datetime.now()

            elif alert.alert_level == 3:
                # 三级响应：紧急通知
                # TODO: 对接短信/电话服务
                if alert.alert_type == 'sms':
                    # self._send_sms(alert.recipient, alert.message)
                    pass
                elif alert.alert_type == 'email':
                    # self._send_email(alert.recipient, alert.title, alert.message)
                    pass

                alert.status = 'sent'
                alert.sent_at = datetime.now()

        except Exception as e:
            alert.status = 'failed'
            alert.error_message = str(e)

        db.commit()

    def simulate_call_120(self, user_id: int, event_id: int = None, duration: float = 0):
        """
        模拟拨打 120 急救电话（演示用）

        真实接入时替换为此方法内的 HTTP 调用，例如：
            requests.post('https://api.example.com/emergency/call', json={...})

        Args:
            user_id: 用户ID
            event_id: 关联事件ID
            duration: 事件持续时长（秒）
        """
        import logging
        logger = logging.getLogger('emergency_120')
        logger.info(
            f"[模拟拨打120] user_id={user_id}, event_id={event_id}, "
            f"duration={duration:.1f}s — 跌倒高风险持续超过40秒，触发紧急呼叫"
        )
        print(f"[紧急呼叫] 模拟拨打120 — 用户 {user_id}, 持续 {duration:.1f}s")

    def acknowledge_alert(self, alert_id: int, user_id: int) -> bool:
        """确认告警"""
        db = next(get_db())
        alert = db.query(AlertHistory).filter_by(id=alert_id).first()
        if alert:
            alert.status = 'acknowledged'
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = user_id
            db.commit()
            return True
        return False

    def mark_sent(self, alert_id: int) -> bool:
        """标记告警已发送"""
        db = next(get_db())
        alert = db.query(AlertHistory).filter_by(id=alert_id).first()
        if alert:
            alert.status = 'sent'
            alert.sent_at = datetime.now()
            db.commit()
            return True
        return False

    def mark_failed(self, alert_id: int, error: str) -> bool:
        """标记告警发送失败"""
        db = next(get_db())
        alert = db.query(AlertHistory).filter_by(id=alert_id).first()
        if alert:
            alert.status = 'failed'
            alert.error_message = error
            db.commit()
            return True
        return False

    # ========== 告警发送接口（预留，暂未接入主流程） ==========

    def send_sms(self, phone: str, message: str) -> dict:
        """
        发送短信告警

        Args:
            phone: 手机号
            message: 短信内容

        Returns:
            {'success': bool, 'message_id': str, 'error': str}

        接入步骤:
            1. 安装 SDK: pip install aliyun-python-sdk-core aliyun-python-sdk-dysmsapi
            2. 在 config.py 配置:
               SMS_ACCESS_KEY_ID = 'xxx'
               SMS_ACCESS_KEY_SECRET = 'xxx'
               SMS_SIGN_NAME = '签名名称'
               SMS_TEMPLATE_CODE = '模板CODE'
            3. 取消下方代码注释并测试
        """
        # from aliyunsdkcore.client import AcsClient
        # from aliyunsdkcore.acs_exception.exceptions import ServerException
        # from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
        # from config import Config

        # try:
        #     client = AcsClient(Config.SMS_ACCESS_KEY_ID, Config.SMS_ACCESS_KEY_SECRET, 'cn-hangzhou')
        #     request = SendSmsRequest.SendSmsRequest()
        #     request.set_PhoneNumbers(phone)
        #     request.set_SignName(Config.SMS_SIGN_NAME)
        #     request.set_TemplateCode(Config.SMS_TEMPLATE_CODE)
        #     request.set_TemplateParam(f'{{"content":"{message}"}}')
        #     response = client.do_action_with_exception(request)
        #     return {'success': True, 'message_id': response.get('BizId'), 'error': None}
        # except ServerException as e:
        #     return {'success': False, 'message_id': None, 'error': str(e)}

        # 暂未接入，返回模拟结果
        print(f"[SMS] 预留接口: 发送至 {phone}, 内容: {message[:50]}...")
        return {'success': True, 'message_id': None, 'error': '接口未接入'}

    def send_email(self, to_email: str, subject: str, body: str) -> dict:
        """
        发送邮件告警

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            body: 邮件正文

        Returns:
            {'success': bool, 'message_id': str, 'error': str}

        接入步骤:
            1. 在 config.py 配置:
               SMTP_SERVER = 'smtp.example.com'
               SMTP_PORT = 465
               SMTP_USERNAME = 'noreply@example.com'
               SMTP_PASSWORD = 'password'
               EMAIL_FROM = 'SilentElderSense <noreply@example.com>'
            2. 取消下方代码注释并测试
        """
        # import smtplib
        # from email.mime.text import MIMEText
        # from email.mime.multipart import MIMEMultipart
        # from config import Config

        # try:
        #     msg = MIMEMultipart()
        #     msg['From'] = Config.EMAIL_FROM
        #     msg['To'] = to_email
        #     msg['Subject'] = subject
        #     msg.attach(MIMEText(body, 'plain', 'utf-8'))

        #     with smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
        #         server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        #         server.sendmail(Config.SMTP_USERNAME, to_email, msg.as_string())

        #     return {'success': True, 'message_id': None, 'error': None}
        # except Exception as e:
        #     return {'success': False, 'message_id': None, 'error': str(e)}

        # 暂未接入，返回模拟结果
        print(f"[Email] 预留接口: 发送至 {to_email}, 主题: {subject}")
        return {'success': True, 'message_id': None, 'error': '接口未接入'}

    def send_app_push(self, user_id: int, title: str, message: str, data: dict = None) -> dict:
        """
        发送应用内推送

        Args:
            user_id: 用户ID
            title: 推送标题
            message: 推送内容
            data: 附加数据（如事件ID、风险等级等）

        Returns:
            {'success': bool, 'error': str}

        接入步骤:
            1. 建立全局 WebSocket 连接管理器（如使用 redis pub/sub）
            2. 在用户登录时注册连接，登出时移除
            3. 调用此方法时通过 user_id 找到对应连接并发送消息

        示例代码:
            from websocket_manager import manager
            await manager.send_to_user(user_id, {
                'type': 'alert',
                'title': title,
                'message': message,
                'data': data
            })
        """
        # 暂未实现 WebSocket 推送管理器
        print(f"[AppPush] 预留接口: 用户 {user_id}, 标题: {title}, 内容: {message[:50]}...")
        return {'success': True, 'error': '接口未接入'}
