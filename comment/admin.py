from django.contrib import admin
from comment.models import Comment

class CommentsAdmin(admin.ModelAdmin):
    '''
    Custom admin for comment model
    '''
    fieldsets = [
      (None, {'fields': ['id','user','content_type','object_id','content_object','comment']}),
      ('Tracking',  {'fields':['ip_address','last_updated_date','creation_date']}),
      ]

    list_display = ('family','user','content_type', 'object_id', 'ip_address','creation_date')
    list_filter = ('creation_date', 'family', 'user')
    date_hierarchy = 'creation_date'
    ordering = ('-creation_date',)
    raw_id_fields = ('user',)
    readonly_fields = ('id', 'last_updated_date', 'creation_date','content_object',)
    search_fields = ['user__name', 'user__email', 'comment']

admin.site.register(Comment, CommentsAdmin)