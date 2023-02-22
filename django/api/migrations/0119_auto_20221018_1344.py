# Generated by Django 3.2.9 on 2022-10-18 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0118_auto_20221018_1240'),
    ]

    operations = [
        migrations.AddField(
            model_name='showcustommodal',
            name='anonymized_google_spreadsheet_id',
            field=models.CharField(blank=True, help_text='Spreadsheet ID where to export modal submissions (with usernames and user ids anonymized).\nMake sure bot has edit access to this spreadsheet. \nSpreadsheet ID can be found in spreadsheet URL - https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0.\nSubmissions are exported daily', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='showselectmenu',
            name='anonymized_google_spreadsheet_id',
            field=models.CharField(blank=True, help_text='Spreadsheet ID where to export menu submissions (with usernames and user ids anonymized).\nMake sure bot has edit access to this spreadsheet. \nSpreadsheet ID can be found in spreadsheet URL - https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0.\nSubmissions are exported daily', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='showcustommodal',
            name='csv_export_is_anonymous',
            field=models.BooleanField(default=False, help_text='Affects only export from Django admin'),
        ),
        migrations.AlterField(
            model_name='showcustommodal',
            name='google_spreadsheet_id',
            field=models.CharField(blank=True, help_text='Spreadsheet ID where to export modal submissions (with visible usernames and user ids).\nMake sure bot has edit access to this spreadsheet. \nSpreadsheet ID can be found in spreadsheet URL - https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0.\nSubmissions are exported daily', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='showselectmenu',
            name='csv_export_is_anonymous',
            field=models.BooleanField(default=False, help_text='Affects only export from Django admin'),
        ),
        migrations.AlterField(
            model_name='showselectmenu',
            name='google_spreadsheet_id',
            field=models.CharField(blank=True, help_text='Spreadsheet ID where to export menu submissions (with visible usernames and user ids).\nMake sure bot has edit access to this spreadsheet. \nSpreadsheet ID can be found in spreadsheet URL - https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0.\nSubmissions are exported daily', max_length=100, null=True),
        ),
    ]
