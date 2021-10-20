from django.contrib import admin

from .models import HomePage, HomePageImage, Notice, NoticeFile


class NoticeFileInLine(admin.TabularInline):
    model = NoticeFile


class NoticeAdmin(admin.ModelAdmin):
    inlines = [
        NoticeFileInLine,
    ]


admin.site.register(Notice, NoticeAdmin)


class HomePageWithImage(admin.TabularInline):
    model = HomePageImage


class HomePageAdmin(admin.ModelAdmin):
    model = HomePage
    inlines = [
        HomePageWithImage
    ]

    def has_add_permission(self, request):
        if self.model.objects.count() > 0:
            return False
        else:
            return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if self.model.objects.count() > 0:
            return False
        else:
            return super().has_delete_permission(request)


admin.site.register(HomePage, HomePageAdmin)
