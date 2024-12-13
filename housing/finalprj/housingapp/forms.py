from django import forms
from .models import Building, Room, Student, CommunityDirector, Lease

class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = '__all__'

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
class CDForm(forms.ModelForm):
    class Meta:
        model = CommunityDirector
        fields = '__all__'
class LeaseForm(forms.ModelForm):
    class Meta:
        model = Lease
        fields = '__all__'