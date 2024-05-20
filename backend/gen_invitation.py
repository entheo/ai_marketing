import string
import random
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from account.models import InvitationCode

def generate_invite_code(length=10):
    """生成一个由大写字母和数字组成的随机邀请码"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_invitation_codes(n):
    """基于请求的数量n生成邀请码，并且保存到数据库中"""
    created_count = 0
    while created_count < n:
        code = generate_invite_code()
        if not InvitationCode.objects.filter(code=code).exists():
            InvitationCode.objects.create(code=code)
            print(f"Created invite code: {code}")
            created_count += 1
        else:
            print(f"Code {code} already exists. Generating a new one.")

if __name__ == '__main__':
    num = input('输入生成数量:')
    number_of_codes = int(num)  # 你想生成的邀请码数量
    create_invitation_codes(number_of_codes)
