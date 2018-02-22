from django import forms

'''
All the forms used in the project are defined here

'''



class NameForm(forms.Form):
	
	#defining all the fields in the form
    resource_name = forms.CharField(label='Resource name', max_length=100)
    lang = forms.CharField(label='Language', max_length=2)
    res_type = forms.CharField(label='Resource type', max_length=1)
    output_format = forms.CharField(label='Output format', max_length=1)
    
