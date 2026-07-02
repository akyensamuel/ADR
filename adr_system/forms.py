from django import forms


class InteractionCheckForm(forms.Form):
    source_drug_name = forms.CharField(
        label='First drug',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Warfarin'}),
    )
    target_drug_name = forms.CharField(
        label='Second drug',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Aspirin'}),
    )


class RecommendationForm(forms.Form):
    drug_name = forms.CharField(
        label='Drug to review',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Metformin'}),
    )


class DatasetImportForm(forms.Form):
    dataset_type = forms.ChoiceField(
        label='Dataset type',
        choices=(
            ('drugbank-drugs', 'DrugBank drugs'),
            ('drugbank-interactions', 'DrugBank interactions'),
            ('sider-reactions', 'SIDER adverse reactions'),
            ('patient-medication', 'Personalized medication dataset'),
            ('meddra-terms', 'MedDRA terminology TSV'),
        ),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    data_file = forms.FileField(
        label='Upload file',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
    )