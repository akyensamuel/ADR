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