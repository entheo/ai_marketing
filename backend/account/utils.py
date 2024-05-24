from .models import Users

def get_current_user(username):
    try:
       user = Users.objects.get(username=username)
    except ObjectDoesNotExist:
        print(f"用户{username}不存在")
        raise ValueError(f"{some_user_id} 用户不存在")
    return user
