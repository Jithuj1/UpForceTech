from django.db import models
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser



class MyAccountManager(BaseUserManager):
    def create_user(self, email, name,   password=None):
        if not email:
            raise ValueError('User must have a username')

        email = self.normalize_email(email)
        user = self.model(
            email = email,
            name = name,
        )

        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, name, password):

        user=self.create_user(email, name, password)

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class CustomUser(AbstractBaseUser):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True, null=False)
    password = models.TextField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


    is_admin  = models.BooleanField(default=False)
    is_staff   = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    is_superuser   = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['name']
    objects = MyAccountManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True
    

class Post(models.Model):
    image = models.ImageField(upload_to='images/')
    title = models.CharField(max_length=50)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    visibility = models.CharField(max_length=50, default='public')
    user_id = models.ForeignKey("mainapp.CustomUser", on_delete=models.CASCADE)
    like_count = models.IntegerField(default=0)


class Like(models.Model):
    user_id = models.ForeignKey("mainapp.CustomUser", on_delete=models.CASCADE)
    post_id = models.ForeignKey("mainapp.Post", on_delete=models.CASCADE)