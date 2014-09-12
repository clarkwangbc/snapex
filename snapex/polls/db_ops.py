from models import *
from django.conf import settings
import uuid
from django.contrib.auth.models import User

'''
    Utilies
'''
def generate_uid():
    return str(uuid.uuid4())[:30]

def generate_uids(number):
    return [generate_uid() for x in range(number)]

'''
    Create Administration
'''
def create_admin(username, password, device_id = None):
    u = User.objects.filter(username=username).exists()
    if u:
        return 1, 'username already exist'
    else:
        u = User(username=username, is_active=True, is_staff=True, is_superuser=True)
        u.set_password(password)
        u.save()
        up = UserProfile(user=u, is_admin=True, is_researcher=True, device_id=device_id)
        up.save()
        return 0, 'admin creation succeeded'

def create_researcher(user):
    '''
        user: string / tuple or list of string / tuple
    '''
    if type(user) == type(str()) or type(user) == type(str())
        user = [user]
        
    if type(user) == type(list()):
        ret = []
        for one_user in user:
            if type(one_user) == type(str()):
                one_user = ["user": user]
            if type(one_user) != type(dict()):
                ret.append(None)
            elif "user" not in one_user:
                ret.append(None)
            else:
                if User.objects.filter(username=one_user).exists():
                    ret.append(None)
                else:
                    u = User(username=one_user["user"], is_active=False, is_staff=False, is_superuser=False)
                    if "password" in user:
                        u.set_password(user["password"])
                    else:
                        u.set_password(settings.DEFAULT_PASSWORD)
                    u.save()
                    up = UserProfile(user=u, is_admin=False, is_researcher=True, device_id='')
                    if "email" in user:
                        up.set_telephone(user["email"])
                    if "telephone" in user:
                        up.set_telephone(user["telephone"])
                    if "organization" in user:
                        up.set_organization(user["organization"])
                    up.save()
                    ret.append(u)
        return 0, ret
    return 1, 'invalid input, string or list of string required'
    

def create_testee(user):
    '''
        user: string or list of string
    '''
    if type(user) == type(str()):
        user = [user]
    if type(user) == type(list()):
        ret = []
        for one_user in user:
            if type(one_user) != type(str()):
                return 1, 'invalid input'
            if User.objects.filter(username=one_user).exists():
                return 1, 'username already exists'
            else:
                u = User(username=one_user, is_active=False, is_staff=False, is_superuser=False)
                u.set_password(settings.DEFAULT_PASSWORD)
                u.save()
                up = UserProfile(user=u, is_admin=False, is_researcher=False, device_id='')
                up.save()
                ret.append(u)
        return 0, ret
    return 1, 'invalid input, string or list of string required'


def get_user_from_secret(secret):
    objs = User.objects.filter(username=secret)
    return objs[0] if objs.exists() else None
            

def get_project_from_pk(pk):
    objs = Project.objects.filter(pk=pk)
    return objs[0] if objs.exists() else None


def get_survey_from_pk(pk):
    objs = Survey.objects.filter(pk=pk)
    return objs[0] if objs.exists() else None


def get_schedule_from_pk(pk):
    objs = Schedule.objects.filter(pk=pk)
    return objs[0] if objs.exists() else None    


def get_plans_from_user(user):
    return user.testee_plans.all()


def get_schedule_from_plan(plan):
    return plan.schedule


def get_project_from_plan(plan):
    return plan.project


def get_survey_from_plan(plan):
    return plan.survey


def get_projects_from_researcher(rs):
    return rs.owner_projects.all()


def get_testees_from_project(project):
    return project.testees.all()


def get_surveys_from_project(project):
    return project.project_surveys.all()


def get_plans_from_project(project):
    return project.project_plans.all()


def get_surveys_from_project(project):
    return project.project_surveys.all()


def get_plan_from_pk(pk):
    objs = Plan.objects.filter(pk=pk)
    return objs[0] if objs.exists() else None


def get_record_from_pk(pk):
    objs = Record.objects.filter(pk=pk)
    return objs[0] if objs.exists() else None


def get_record_from_pk(pk):
    objs = Record.objects.filter(pk=pk)
    return objs[0] if objs.exists() else None


def add_testee_to_project(testee, project):
    if ProjectTesteeMembership.objects.filter(project=project, testee=testee).exists():
        return 1, 'testee already in project'
    else:
        ptm = ProjectTesteeMembership(project=project, testee=testee, alias='')
        ptm.save()
        return 0, ptm


def activate_user(secret):
    user = get_user_from_secret(secret)
    if user:
        user.is_active = True
        user.save()
        return 0
    else:
        return 1


def create_new_testees(number):
    user_names = generate_uids(number)
    new_testees = None
    for i in range(3):
        st, new_testees = create_testee(user_names)
        if st==0:
            break
        else:
            user_names = generate_uids(init)
        if i==3:
            return 1, 'create project failed due to lack of available usernames'

    return 0, new_testees

# project
def create_project(owner, name, subject='', init=0, researchers=[]):
    st, new_testees = create_new_testees(init)
    if not type(new_testees) == type(list()):
        return 1, 'create_testee failed'

    p = Project(owner=owner, name=name, subject=subject)
    p.save()

    for testee in new_testees:
        add_testee_to_project(testee, p)
    
    return 0, p


def send_plan(plan):
    try:
        device_id = plan.testee.user_profile.device_id
        if device_id != '':
            user_id = device_id.split(',')[0]
            channel_id = device_id.split(',')[1]
            msg = {'title':'Snap Experience', 'description': 'You have new plans!'}
            import api.bd_push as bd_push
            ret = bd_push.push_msg(user_id, int(channel_id), msg)
            if ret[0]==0:
                plan.is_sent = True
                plan.save()
            return ret
        else:
            return 1, 'need a valid device_id'
    except Exception as e:
        return 1, str(e)
    