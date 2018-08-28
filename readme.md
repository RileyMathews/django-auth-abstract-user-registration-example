This repo is a barebones example of how to overwrite the default django authenticated user by inheriting from AbstractUser. Specifically looking how we can add additional fields to the user model, and tell django how we want that information to be created on user registration. 

## required packages
The following packages were installed to make this project work as intended
```
pip install django djangorestframework django-rest-auth django-allauth
```
These installs will install a few other dependencies. 

add the following apps to your installed apps...
```
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_auth',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    'rest_framework.authtoken',
    'django.contrib.sites',
    ...
]
```

You will also need to add these two lines to your settings.py file to keep django from yelling at you about missing configuration.
```
SITE_ID = 1

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## setup your user model

### create your custom user model
Start by creating a custom model that inherits from the AbstractUser class from django.contrib.auth.models as is done in this repos api.models.user.py file.

This model will inherit all properties of the default django user (the same one that is created when you run python manage.py createsuperuser). But has the benefit of allowing you to add additional fields to the model as is demonstrated by our user models 'added_field' property. 

### make your model the user model
We have our model but django doesn't know that we intend to use it as our prime user model. We have to tell it by adding the following line in settings.py
```
AUTH_USER_MODEL = 'api.User'
```
If you named your app or model something different point the value to your user model instead. 

At this point you can initialize your database by running 
```
python manage.py makemigrations api #or your app name
python manage.py makemigrations allauth #required for some backend user things
python manage.py migrate
```

Now django knows to use our custom user model in place of its default user model. But the functionality should remain mostly the same since it inherits all properties of the default user. 

If you want to see it in action create a django superuser from the command line, and register your custom user model with the admin panel in the apps admin.py file.
You can then login to the admin interface and view your newly created superuser. It should have any extra fields you defined on your custom user model. Django is now using your custom user model in place of the default. 

At this point you can go ahead and create a basic serializer and viewset for your user model that exposes as much public information you want available about your users. 

Thats great so far, but our client side users don't have access to createsuperuser, and simply having them post to a simple user serializer and viewset will not hash their password or do any of the other django magic we want on user registration. So we need to expose a registration endpoint in our api to allow users to register users for themselves.

### simple registration
If you don't need your additional abstract user fields to be defined upon user registration you can simply add the default views for register and login to your urls as shown in this repos api.urls.py file

```
router = DefaultRouter()

router.register('user', views.UserViewset)

urlpatterns = [
    url('auth/', include('rest_auth.urls')),
    url('auth/registration/', include('rest_auth.registration.urls'))
] + router.urls
```

This will allow you to post information to domainofapi.com/auth/registration to create a django user the right way. If everything works it will send back your json web token as a response. You can then visit .../auth/login/ or .../auth/logout/ to get or delete a users web token. 

### but what about my custom fields
If your user model is extending AbstractUser, its likely that you are defining things that need to be on the user object upon creation. With everything up to this point the only thing we can define upon registration is username, email, and password. There are two levels of how we can add additional information to this

#### adding fields that are included in base user
If all you want to do is add a field that is already on django's base user model (which can be found in the docs here: https://docs.djangoproject.com/en/2.1/ref/contrib/auth/), all you have to do is override the default serializer. 

Start by creating a new serializer class using this repos api.serializers.user_registration_serializer.py as an example, you can ignore the save() method thats defined for now. 

```
class UserRegistrationSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'username': self.validated_data.get('username', ''),
            'email': self.validated_data.get('email', '')
        }
```

Note we do not need to include password here. That gets handled by some other django magic method. Here we are only saying that we also want to be able to define first and last name upon user registration, and by including required=True the api will not allow you to post to this endpoint without those fields at all. 

Now we need to once again tell django that we are choosing to override a default with our own custom class. Go into settings.py again and add the following lines. 

```
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'api.serializers.UserRegistrationSerializer'
}
```

Once again renaming the path based on your app and serialzer name. 

#### adding our custom fields
In this example code we are defining an additional field of 'added_field' in our custom user model. This field is still not being populated on creation. First add information about it like we did for first name and last name in the above code. 

```
class UserRegistrationSerializer(RegisterSerializer):
    added_field = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def get_cleaned_data(self):
        return {
            'added_field': self.validated_data.get('added_field', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'username': self.validated_data.get('username', ''),
            'email': self.validated_data.get('email', '')
        }
```

But that isn't enough, django still doesn't know that we actually want that information. We need to overide the save method by doing the following

```
    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])

        # add custom fields
        user.added_field = self.cleaned_data.get('added_field')

        user.save()

        return user
```

Note: some of the methods called here need to be imported as is done in the actual file api.serializers.user_registration_serializer.py in this repo. 

Now if everything has been done correctly up to this point. you should be able to navigate to the registration url in the browser and post a new user that will save any additional information you defined upon user registration. 