"""
模拟数据生成脚本
用于生成测试数据：用户、事件、告警配置、告警历史
"""
import os
import sys
import random
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATA_DIR
from auth.models import Base, User
from events.models import Event
from alerts.models import AlertConfig, AlertHistory

DB_NAME = "db.sqlite3"
db_path = os.path.join(DATA_DIR, DB_NAME)

# 创建引擎和会话
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
db = Session()


def random_datetime(days_back=30):
    """生成过去N天内的随机时间"""
    now = datetime.utcnow()
    random_days = random.randint(0, days_back)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    return now - timedelta(days=random_days, hours=random_hours, minutes=random_minutes)


def generate_users(count=5):
    """生成用户数据"""
    print(f"[1/4] 生成 {count} 个用户...")

    users = []
    usernames = ['zhangsan', 'lisi', 'wangwu', 'zhaoliu', 'sunqi', 'zhouba', 'wujiu', 'zhengshi']

    # 检查管理员是否存在
    admin = db.query(User).filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('123456')
        db.add(admin)
        db.commit()
    users.append(admin)

    # 生成其他用户
    for i in range(count - 1):
        username = usernames[i] if i < len(usernames) else f'user{i+1}'
        # 检查用户是否已存在
        existing = db.query(User).filter_by(username=username).first()
        if existing:
            users.append(existing)
            continue
        user = User(
            username=username,
            email=f'{username}@example.com',
            is_admin=random.choice([True, False])
        )
        user.set_password('123456')
        db.add(user)
        users.append(user)

    db.commit()
    print(f"      已准备 {len(users)} 个用户")
    return users


def generate_events(users, count=50):
    """生成事件数据"""
    print(f"[2/4] 生成 {count} 条事件...")

    event_types = ['FALL', 'STATIC', 'NIGHT_ABNORMAL']
    risk_levels = ['HIGH', 'MEDIUM', 'LOW']
    statuses = ['pending', 'confirmed', 'false_alarm']

    events = []
    for i in range(count):
        user = random.choice(users)
        event_type = random.choice(event_types)
        risk_level = random.choice(risk_levels)

        # 根据事件类型设置不同的持续时间
        if event_type == 'FALL':
            duration = random.uniform(1.0, 10.0)
        elif event_type == 'STATIC':
            duration = random.uniform(60.0, 600.0)  # 1-10分钟
        else:  # NIGHT_ABNORMAL
            duration = random.uniform(30.0, 300.0)

        start_time = random_datetime(30)
        end_time = start_time + timedelta(seconds=duration)

        event = Event(
            user_id=user.id,
            video_id=f'vid_{random.randint(1000, 9999)}',
            person_id=random.randint(0, 5),
            event_type=event_type,
            risk_level=risk_level,
            start_time=start_time,
            end_time=end_time,
            duration=round(duration, 2),
            frame_count=random.randint(5, 100),
            status=random.choice(statuses),
            notes=random.choice(['', '已确认处理', '误报', '需要关注', '已通知家属', ''])
        )
        db.add(event)
        events.append(event)

        if (i + 1) % 10 == 0:
            print(f"      进度: {i+1}/{count}")

    db.commit()
    print(f"      已生成 {len(events)} 条事件")
    return events


def generate_alert_configs(users):
    """生成告警配置"""
    print(f"[3/4] 生成告警配置...")

    configs = []
    for user in users:
        config = AlertConfig(
            user_id=user.id,
            high_alert_methods='sms,email,app',
            medium_alert_methods='email,app',
            low_alert_methods='app',
            emergency_contact=f'紧急联系人{user.id}',
            emergency_phone=f'138{random.randint(10000000, 99999999)}',
            email=user.email,
            quiet_hours_start='22:00',
            quiet_hours_end='07:00',
            bypass_quiet_hours=True
        )
        db.add(config)
        configs.append(config)

    db.commit()
    print(f"      已生成 {len(configs)} 条告警配置")
    return configs


def generate_alert_histories(users, events, count=30):
    """生成告警历史"""
    print(f"[4/4] 生成 {count} 条告警历史...")

    alert_types = ['sms', 'email', 'app', 'push']
    statuses = ['pending', 'sent', 'failed', 'acknowledged']

    histories = []
    for i in range(count):
        user = random.choice(users)
        event = random.choice(events) if events else None

        risk_level = random.choice(['HIGH', 'MEDIUM', 'LOW'])
        event_type = random.choice(['FALL', 'STATIC', 'NIGHT_ABNORMAL'])

        # 根据风险等级确定告警级别
        if risk_level == 'HIGH':
            alert_level = 3
        elif risk_level == 'MEDIUM':
            alert_level = 2
        else:
            alert_level = 1

        alert_type = random.choice(alert_types)
        status = random.choice(statuses)

        title_map = {
            'FALL': '跌倒检测告警',
            'STATIC': '长时间静止告警',
            'NIGHT_ABNORMAL': '夜间异常活动告警'
        }
        risk_map = {
            'HIGH': '高风险',
            'MEDIUM': '中风险',
            'LOW': '低风险'
        }

        history = AlertHistory(
            user_id=user.id,
            event_id=event.id if event else None,
            alert_level=alert_level,
            alert_type=alert_type,
            risk_level=risk_level,
            event_type=event_type,
            title=f"【{risk_map[risk_level]}】{title_map[event_type]}",
            message=f"检测到{title_map[event_type]}，风险等级：{risk_map[risk_level]}，请及时关注。",
            status=status,
            recipient=f'138{random.randint(10000000, 99999999)}' if alert_type == 'sms' else user.email,
            sent_at=random_datetime(7) if status in ['sent', 'acknowledged'] else None,
            acknowledged_at=random_datetime(3) if status == 'acknowledged' else None
        )
        db.add(history)
        histories.append(history)

    db.commit()
    print(f"      已生成 {len(histories)} 条告警历史")
    return histories


def print_summary():
    """打印数据统计"""
    print("\n" + "="*50)
    print("数据生成完成！统计如下：")
    print("="*50)

    user_count = db.query(User).count()
    event_count = db.query(Event).count()
    alert_config_count = db.query(AlertConfig).count()
    alert_history_count = db.query(AlertHistory).count()

    print(f"  用户数量:       {user_count}")
    print(f"  事件数量:       {event_count}")
    print(f"  告警配置数量:   {alert_config_count}")
    print(f"  告警历史数量:   {alert_history_count}")

    # 事件统计
    print("\n事件类型分布:")
    for event_type in ['FALL', 'STATIC', 'NIGHT_ABNORMAL']:
        count = db.query(Event).filter(Event.event_type == event_type).count()
        print(f"  {event_type}: {count}")

    print("\n风险等级分布:")
    for risk_level in ['HIGH', 'MEDIUM', 'LOW']:
        count = db.query(Event).filter(Event.risk_level == risk_level).count()
        print(f"  {risk_level}: {count}")

    print("\n默认登录账号: admin / 123456")
    print("="*50)


def main():
    """主函数"""
    print("="*50)
    print("开始生成模拟数据...")
    print("="*50 + "\n")

    # 生成数据
    users = generate_users(5)
    events = generate_events(users, 50)
    generate_alert_configs(users)
    generate_alert_histories(users, events, 30)

    # 打印统计
    print_summary()

    db.close()


if __name__ == '__main__':
    main()
