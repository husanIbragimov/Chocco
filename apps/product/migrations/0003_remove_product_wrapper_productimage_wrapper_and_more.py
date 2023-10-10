# Generated by Django 4.2.3 on 2023-09-28 11:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_author_printed_tag_product_format_product_isbn_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='wrapper',
        ),
        migrations.AddField(
            model_name='productimage',
            name='wrapper',
            field=models.CharField(blank=True, choices=[('qattiq', 'qattiq'), ('yumshoq', 'yumshoq')], max_length=25, null=True, verbose_name='Muqova'),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_type',
            field=models.CharField(choices=[('book', 'Book'), ('clothing', 'Clothing'), ('product', 'Product')], default='product', max_length=25),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_images', to='product.color'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_images', to='product.product'),
        ),
    ]