from django.contrib.auth.models import User
from django.db import models
from ckeditor.fields import RichTextField
from django.db.models import Avg
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from mptt.models import MPTTModel
from apps.base.models import BaseAbstractDate, Variant
from colorfield.fields import ColorField
from django.db.models.signals import post_save
from django.dispatch import receiver
from rembg import remove
from PIL import Image

STATUS = (
    ('NEW', 'NEW'),
    ('HOT', 'HOT'),
    ('BEST SELL', 'BEST SELL'),
    ('SALE', 'SALE'),
)

LANGUAGE = (
    ('english', 'english'),
    ('russian', 'russian'),
    ('uzbek', 'uzbek'),
)

YOZUV = (
    ('krill', 'Krill'),
    ('lotin', 'Lotin'),

)

MUQOVA = (
    ('qattiq', 'qattiq'),
    ('yumshoq', 'yumshoq'),
)

PRODUCT_TYPE = (
    ('book', 'Book'),
    ('clothing', 'Clothing'),
    ('product', 'Product')
)


class BannerDiscount(BaseAbstractDate):
    title = models.TextField(null=True)
    image = models.ImageField(upload_to='sales', null=True)
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def product_id(self):
        return self.product_set.last()

    def __str__(self):
        return f'{self.deadline}'

    # def get_absolute_url(self):
    #     return reverse("")


class Currency(BaseAbstractDate):
    amount = models.FloatField()

    def __str__(self):
        return str(self.amount)


class Advertisement(BaseAbstractDate):
    icon = models.ImageField(upload_to='advertisement/icons/', null=True, blank=True)
    title = models.CharField(max_length=223, null=True)
    description = RichTextField(null=True, blank=True)
    banner_image = models.ImageField(upload_to='advertisement/banners/', null=True)

    def __str__(self):
        if self.title:
            return self.title
        return 'None title'


class Category(MPTTModel, BaseAbstractDate):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='Parent Category',
                               limit_choices_to={'is_active': True},
                               related_name='children', null=True, blank=True, )
    title = models.CharField(max_length=50)
    icon = models.ImageField(upload_to='category', null=True, blank=True)
    product_type = models.CharField(max_length=25, choices=PRODUCT_TYPE, default='product')
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
        order_insertion_by = ['title']

    def __str__(self):
        return self.title


class Banner(BaseAbstractDate):
    desc = RichTextField(null=True, blank=True)
    title = models.CharField(max_length=223, null=True, blank=True)
    image = models.ImageField(upload_to='banner', null=True, blank=True)

    def __str__(self):
        return self.title


class Brand(BaseAbstractDate):
    title = models.CharField(max_length=223)
    product_type = models.CharField(max_length=25, choices=PRODUCT_TYPE, default='product')

    def __str__(self):
        return self.title


class Color(BaseAbstractDate):
    COLOR_PALETTE = [
        ("#ff0000", "qizil",),
        ("#ffa500", "jigar rang",),
        ("#ffff00", "sariq",),
        ("#008000", "yashil",),
        ("#0000ff", "ko'k",),
        ("#4b0082", "binafsha",),
        ("#ee82ee", "pushti",),
    ]
    name = ColorField(samples=COLOR_PALETTE)
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title

    def colored_name(self):
        return format_html(
            '<span style="color: #{};">{}</span>',
            self.name,
        )


class Size(BaseAbstractDate):
    name = models.CharField(max_length=50)
    product_type = models.CharField(max_length=25, choices=PRODUCT_TYPE, default='product')

    def __str__(self):
        return self.name


class Author(BaseAbstractDate):
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        if self.name:
            return self.name
        return 'No name'


class Product(BaseAbstractDate):
    # product and clothing
    banner_discount = models.ForeignKey(BannerDiscount, on_delete=models.SET_NULL, null=True, blank=True)
    advertisement = models.ForeignKey(Advertisement, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(choices=STATUS, default='NEW', max_length=10, null=True, blank=True)
    title = models.TextField(null=True)
    category = models.ManyToManyField(Category, blank=True,
                                      limit_choices_to={'is_active': True, 'parent__isnull': False})
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ManyToManyField(Size, blank=True)
    percentage = models.FloatField(default=0, null=True, blank=True)
    discount = models.FloatField(default=0, null=True, blank=True)
    view = models.IntegerField(default=0, null=True, blank=True)
    description = RichTextField(null=True, blank=True)
    availability = models.IntegerField(default=0, null=True, blank=True)
    has_size = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, db_index=True)
    product_type = models.CharField(max_length=25, choices=PRODUCT_TYPE, default='product')
    # book
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.CharField(max_length=25, choices=LANGUAGE, default='uzbek')
    yozuv = models.CharField(max_length=25, choices=YOZUV, default='lotin')

    @property
    def mid_rate(self):
        result = Rate.objects.filter(product=self.id).aggregate(avarage=Avg("rate"))
        if result['avarage']:
            return round(result['avarage'], 1)
        else:
            return 0.0

    @property
    def mid_rate_percent(self):
        result = Rate.objects.filter(product=self.id).aggregate(avarage=Avg("rate"))
        if result['avarage']:
            percent = result['avarage'] * 100 / 5
            return percent
        else:
            return 0.0

    @property
    def get_discount_price(self):
        if self.percentage:
            discount_sell = self.product_images.first().price - (
                    self.product_images.first().price * (self.percentage / 100))
            self.discount = discount_sell
            self.save()
            return discount_sell
        return 0

    def __str__(self):
        if self.title:
            return self.title
        return f'{self.id}'

    def image_tag(self):
        if not self.product_images.all().first().image.url:
            return "No Image"
        return mark_safe('<img src="{}" height="80"/>'.format(self.product_images.all().first().image.url))

    image_tag.short_description = 'Mahsulot rasmi'

    # image_tag.allow_tags = True

    @property
    def price_uzs(self):
        price = int(self.product_images.first().price * Currency.objects.last().amount)
        return price  # "%s%s" % (intcomma(int(price)), ("%0.2f" % price)[-3:])

    @property
    def discount_uzs(self):
        discount = int(self.discount * Currency.objects.last().amount)
        return discount  # f"%s%s" % (intcomma(int(discount)), ("%0.2f" % discount)[-3:])

    @property
    def monthly_uzs(self):
        active_variant = Variant.objects.all().last()
        total = self.price_uzs + ((active_variant.percent * self.price_uzs) / 100)
        monthly = total / active_variant.duration
        return int(monthly)  # f"%s%s" % (intcomma(int(discount)), ("%0.2f" % discount)[-3:])

    @property
    def total_uzs(self):
        active_variant = Variant.objects.last().percent
        total = self.price_uzs + ((active_variant * self.price_uzs) / 100)
        return int(total)  # f"%s%s" % (intcomma(int(discount)), ("%0.2f" % discount)[-3:])


class ProductImage(BaseAbstractDate):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images', null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='product_images', null=True, blank=True)
    wrapper = models.CharField(max_length=25, choices=MUQOVA, null=True, blank=True, verbose_name='Muqova')
    image = models.FileField(upload_to='products', null=False, blank=False)
    price = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Image of {self.product}'

    @property
    def price_uzs(self):
        price = int(self.price * Currency.objects.last().amount)
        return price  # "%s%s" % (intcomma(int(price)), ("%0.2f" % price)[-3:])

    @property
    def total_uzs(self):
        variants = Variant.objects.all().order_by('duration')
        active_variant = variants.last()
        total = self.price_uzs + ((active_variant.percent * self.price_uzs) / 100)
        return int(total)  # f"%s%s" % (intcomma(int(discount)), ("%0.2f" % discount)[-3:])
    
    @property
    def image_url(self):
        return self.image.url 


class AdditionalInfo(BaseAbstractDate):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_info')
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=225, null=True, blank=True)

    def __str__(self):
        return self.title


class Rate(BaseAbstractDate):
    RATE = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_rate")
    rate = models.IntegerField(choices=RATE, default=0)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'rate of {self.user}'

    @property
    def rate_percent(self):
        return round(self.rate * 100 / 5, 1)

@receiver(post_save, sender=ProductImage)
def product_post_save(sender, instance, created, **kwargs):
    try:
        input_image_path = instance.image.path
        input_image = Image.open(input_image_path)
        output_image = remove(input_image)
        
        # Use pure white for the background color in RGB mode
        background_color = (247,243,230)

        output_with_background = Image.new(mode="RGB", size=output_image.size, color=background_color)
        output_with_background.paste(output_image, (0, 0),output_image)
        output_with_background.save(input_image_path)
        
    except Exception as e:
        return f'{e}'

