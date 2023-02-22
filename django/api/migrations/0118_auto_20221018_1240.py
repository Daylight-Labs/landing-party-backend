# Generated by Django 3.2.9 on 2022-10-18 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0117_auto_20221006_2106'),
    ]

    operations = [
        migrations.AddField(
            model_name='guidedflow',
            name='anonymized_google_spreadsheet_id',
            field=models.CharField(blank=True, help_text='Spreadsheet ID where to export menu/modal submissions (with usernames and user ids anonymized).\nMake sure bot has edit access to this spreadsheet. \nSpreadsheet ID can be found in spreadsheet URL - https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0.\nSubmissions are exported daily', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='guidedflow',
            name='google_spreadsheet_id',
            field=models.CharField(blank=True, help_text='Spreadsheet ID where to export menu/modal submissions (with visible usernames and user ids).\nMake sure bot has edit access to this spreadsheet. \nSpreadsheet ID can be found in spreadsheet URL - https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0.\nSubmissions are exported daily', max_length=100, null=True),
        ),
    ]
