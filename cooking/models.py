from django.db import models

# Create your models here.
class Ingredient(models.Model):
    ingredient_name = models.CharField(max_length=50)
    ingredient_description = models.CharField(max_length=300)
    ingredient_effect = models.CharField(max_length=20)
    ingredient_color = models.CharField(max_length=10)
    ingredient_weight = models.IntegerField()
    ingredient_coefficient = models.IntegerField()

    def __str__(self):
        return self.ingredient_name

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        db_table = 'soup_ingredient_info'   # Название таблички в БД


class UserInfo(models.Model):
    user_name = models.CharField(max_length=20)
    user_img = models.CharField(max_length=100)
    user_email = models.CharField(max_length=30)
    user_password = models.CharField(max_length=50)
    user_soup_list = models.CharField(max_length=300)
    user_secret = models.CharField(max_length=50, default=" ")

    def __str__(self):
        return self.user_name

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
