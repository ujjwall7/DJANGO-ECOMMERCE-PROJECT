from django.db import models
from django.urls import reverse


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'category'            #admin select name example  Select category to change
        verbose_name_plural = 'categories'    #admin model name

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])             # products_by_category =url name

    def __str__(self):
        return self.category_name
