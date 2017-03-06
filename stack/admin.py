from django.contrib import admin
from django.contrib.admin import ModelAdmin

from stack.models import Stack, Company, Programmer, GitHubInfo, Job, Category


class StackAdmin(ModelAdmin):
    list_display = ("id", "title", "slug", "created")
    list_display_links = ("id",)
    exclude = ('description',)
    filter_horizontal = ("category",)


class CompanyAdmin(ModelAdmin):
    filter_horizontal = ("stacks", "jobs",)

admin.site.register(Stack, StackAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Category)
admin.site.register(Programmer)
admin.site.register(GitHubInfo)
admin.site.register(Job)
