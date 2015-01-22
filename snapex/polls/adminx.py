import xadmin
from xadmin import views
from models import *
from xadmin.layout import *

from xadmin.plugins.inline import Inline
from xadmin.plugins.batch import BatchChangeAction

class BaseSetting(object):
    enable_themes = False
    use_bootswatch = True
    pass

xadmin.site.register(views.BaseAdminView, BaseSetting)

class GlobeSetting(object):
    globe_search_models = [Project, Survey, UserProfile]
    globe_models_icon = {
        Project: 'cloud', Survey: 'laptop', UserProfile: 'cloud'
    }
    pass
    
xadmin.site.register(views.CommAdminView, GlobeSetting)

#class MaintainInline(object):
 #   model = MaintainLog
  #  extra = 1
   # style = "accordion"
    
class SurveyAdmin(object):
    list_display = ('name' , 'logo', 'date_created')
    list_display_links = ('name',)
    wizard_form_list = [
        
    ]
    search_fields = ['name']
    relfield_style = 'fk-ajax'
    reversion_enable = False
    
    actions = [BatchChangeAction, ]
    batch_fields = ('create_time',)
    pass

#xadmin.site.register(Test)
xadmin.site.register(AnswerEntry)
#xadmin.site.register(Survey, SurveyAdmin)
#xadmin.site.register(User)

#xadmin.site.register(Testee)
#xadmin.site.register(Page)
#xadmin.site.register(QuestionEntry)
#xadmin.site.register(Schedule)
#xadmin.site.register(Plan)
#xadmin.site.register(Record)
