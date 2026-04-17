"""
模拟数据生成脚本

生成完整的演示数据：平台用户、社区组、普通用户、事件
"""
import os
import sys
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import DATA_DIR
from auth.models import Base, User
from platform_org.models import CommunityGroup
from events.models import Event

DB_NAME = "db.sqlite3"
db_path = os.path.join(DATA_DIR, DB_NAME)

engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
db = Session()

# ── 演示数据配置 ──────────────────────────

PLATFORM_USER = {
    'username': 'plat',
    'password': '123456',
    'org_name': '安心养老服务平台',
    'org_description': '专注于社区居家养老安全监测的综合服务平台',
    'org_contact_name': '张经理',
    'org_contact_phone': '13800138000',
}

COMMUNITY_GROUPS = [
    {'name': '阳光花园社区', 'description': '位于城东的成熟社区，以退休职工为主', 'address': '城东区阳光花园路88号'},
    {'name': '翠竹苑社区', 'description': '城西新建社区，配套完善', 'address': '城西区翠竹大道166号'},
    {'name': '和平里社区', 'description': '老城区传统社区，以独居老人居多', 'address': '老城区和平里胡同12号'},
]

USERS_PER_GROUP = (2, 5)
EVENTS_PER_USER = (30, 60)
DAYS_BACK = 30

EVENT_TYPES = ['FALLEN', 'STILLNESS', 'NIGHT_ABNORMAL']
STATUSES = ['pending', 'confirmed', 'false_alarm']
STATUS_WEIGHTS = [0.3, 0.5, 0.2]


def random_dt(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def clear_data():
    print("[0] 清空数据...")
    db.query(Event).delete()
    db.query(User).filter(User.role == 'user').delete()
    db.query(CommunityGroup).delete()
    db.query(User).filter(User.role == 'platform').delete()
    db.commit()


def ensure_admin():
    admin = db.query(User).filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com', is_admin=True, role='admin')
        admin.set_password('123456')
        db.add(admin)
        db.commit()
    print(f"    admin / 123456 (管理员)")


def create_platform_user():
    print("[1] 创建平台用户...")
    p = User(
        username=PLATFORM_USER['username'],
        role='platform',
        org_name=PLATFORM_USER['org_name'],
        org_description=PLATFORM_USER['org_description'],
        org_contact_name=PLATFORM_USER['org_contact_name'],
        org_contact_phone=PLATFORM_USER['org_contact_phone'],
    )
    p.set_password(PLATFORM_USER['password'])
    db.add(p)
    db.commit()
    print(f"    {PLATFORM_USER['username']} / {PLATFORM_USER['password']} ({PLATFORM_USER['org_name']})")
    return p


def create_community_groups(platform_user):
    print("[2] 创建社区组...")
    groups = []
    for cfg in COMMUNITY_GROUPS:
        g = CommunityGroup(
            platform_user_id=platform_user.id,
            name=cfg['name'],
            description=cfg.get('description'),
            address=cfg.get('address'),
        )
        db.add(g)
        groups.append(g)
    db.commit()
    for g in groups:
        print(f"    {g.name}")
    return groups


def create_users(groups):
    print("[3] 创建普通用户...")
    users = []
    # 默认测试用户，不绑定任何社区组
    test = User(username='user', role='user')
    test.set_password('123456')
    db.add(test)
    users.append((test, None))
    print(f"    user / 123456 (未绑定社区组)")
    idx = 1
    for g in groups:
        count = random.randint(*USERS_PER_GROUP)
        for _ in range(count):
            username = f'user{idx}'
            u = User(
                username=username,
                role='user',
                community_group_id=g.id,
            )
            u.set_password('123456')
            db.add(u)
            users.append((u, g))
            idx += 1
    db.commit()
    for u, g in users:
        print(f"    {u.username} / 123456 → {g.name if g else '未绑定'}")
    return users


def generate_events(users):
    print("[4] 生成事件数据...")
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=DAYS_BACK)
    total = 0

    for u, g in users:
        count = random.randint(*EVENTS_PER_USER)
        for _ in range(count):
            event_type = random.choice(EVENT_TYPES)
            start_time = random_dt(start_dt, end_dt)

            if event_type == 'FALLEN':
                risk_level = random.choices(['MEDIUM', 'HIGH'], weights=[0.4, 0.6])[0]
                duration = random.uniform(2.0, 15.0)
            elif event_type == 'STILLNESS':
                risk_level = random.choices(['LOW', 'MEDIUM'], weights=[0.5, 0.5])[0]
                duration = random.uniform(30.0, 300.0)
            else:
                risk_level = 'MEDIUM'
                duration = random.uniform(60.0, 180.0)

            status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
            notes = {
                'pending': '',
                'confirmed': random.choice(['已确认', '已通知家属', '已处理']),
                'false_alarm': random.choice(['误报', '宠物活动', '光线变化']),
            }[status]

            db.add(Event(
                user_id=u.id,
                video_id=f"vid_{random.randint(1000, 9999)}",
                person_id=random.randint(0, 3),
                event_type=event_type,
                risk_level=risk_level,
                start_time=start_time,
                end_time=start_time + timedelta(seconds=duration),
                frame_count=int(duration * 25 * random.uniform(0.8, 1.2)),
                status=status,
                notes=notes,
            ))
            total += 1

    db.commit()
    print(f"    共生成 {total} 条事件（时间范围：{start_dt.strftime('%m-%d')} ~ {end_dt.strftime('%m-%d')}）")
    return total


def print_summary(users, total_events):
    print("\n" + "=" * 50)
    print("数据生成完成")
    print("=" * 50)
    print(f"  平台用户: {PLATFORM_USER['username']} / {PLATFORM_USER['password']}")
    print(f"  管理员:   admin / 123456")
    print(f"  社区组:   {len(COMMUNITY_GROUPS)} 个")
    print(f"  普通用户: {len(users)} 个 (密码均为 123456)")
    print(f"  事件总数: {total_events} 条")
    print("=" * 50)


def main():
    print("生成演示数据...\n")
    clear_data()
    ensure_admin()
    platform_user = create_platform_user()
    groups = create_community_groups(platform_user)
    users = create_users(groups)
    total = generate_events(users)
    print_summary(users, total)
    db.close()


if __name__ == '__main__':
    main()
