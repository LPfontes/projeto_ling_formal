from django import forms

class AutomatoForm(forms.Form):
    alfabeto = forms.CharField(
        label='Alfabeto', 
        help_text='Separe as letras por vírgula (ex: a,b,c,d)',
        widget=forms.TextInput(attrs={'placeholder': 'a,b,c,d'})
    )
    
    estados = forms.CharField(
        label='Estados',
        help_text='Separe os estados por vírgula (ex: q0,q1,q2)',
        widget=forms.TextInput(attrs={'placeholder': 'q0,q1,q2'})
    )
    
    inicial = forms.CharField(
        label='Estado Inicial',
        help_text='Informe o estado inicial (ex: q0)',
        widget=forms.TextInput(attrs={'placeholder': 'q0'})
    )
    
    finais = forms.CharField(
        label='Estados Finais',
        help_text='Separe os estados finais por vírgula (ex: q1,q2)',
        widget=forms.TextInput(attrs={'placeholder': 'q1,q2'})
    )
    
    transicoes = forms.CharField(
        label='Transições',
        help_text='Informe as transições no formato (ex: q0,q1,a)',
        widget=forms.Textarea(attrs={'placeholder': 'q0,q1,a\nq1,q2,b'})
    )