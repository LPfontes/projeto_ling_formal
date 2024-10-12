from django import forms

class AutomatoForm(forms.Form):
    alfabeto = forms.CharField(
        label='Alfabeto', 
        required=False,  # Deixar como opcional
        help_text='Separe as letras por vírgula (ex: 0,1)',
        widget=forms.TextInput(attrs={'placeholder': '0,1'})
    )
    
    estados = forms.CharField(
        label='Estados',
        required=False,  # Deixar como opcional
        help_text='Separe os estados por vírgula (ex: q0,q1,q2)',
        widget=forms.TextInput(attrs={'placeholder': 'q0,q1,q2'})
    )
    
    inicial = forms.CharField(
        label='Estado Inicial',
        required=False,  # Deixar como opcional
        help_text='Informe o estado inicial (ex: q0)',
        widget=forms.TextInput(attrs={'placeholder': 'q0'})
    )
    
    finais = forms.CharField(
        label='Estados Finais',
        required=False,  # Deixar como opcional
        help_text='Separe os estados finais por vírgula (ex: q1,q2)',
        widget=forms.TextInput(attrs={'placeholder': 'q1,q2'})
    )
    
    transicoes = forms.CharField(
        label='Transições',
        required=False,  # Deixar como opcional
        help_text='Informe as transições no formato (ex: q0,q1,0)',
        widget=forms.Textarea(attrs={'placeholder': 'q0,q1,0\nq1,q2,0'})
    )

    arquivo_txt = forms.FileField(
        label="Upload de Arquivo do AFD (.txt)",
        required=False,  # Arquivo também opcional
    )

    def clean(self):
        cleaned_data = super().clean()
        arquivo_txt = cleaned_data.get('arquivo_txt')

        # Se o arquivo não for enviado, os campos manuais devem ser obrigatórios
        if not arquivo_txt:
            alfabeto = cleaned_data.get('alfabeto')
            estados = cleaned_data.get('estados')
            inicial = cleaned_data.get('inicial')
            finais = cleaned_data.get('finais')
            transicoes = cleaned_data.get('transicoes')

            if not all([alfabeto, estados, inicial, finais, transicoes]):
                raise forms.ValidationError('Preencha todos os campos ou envie um arquivo .txt.')
        return cleaned_data