from django import forms

class NotificationAddForm(forms.ModelForm):
    all_users = forms.BooleanField(label = 'Create for all users', required = False)
    class Meta:
        fields = ('user', 'message','read')

