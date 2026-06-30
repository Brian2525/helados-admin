from django import forms


class TailwindModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        base_class = (
            "w-full rounded-lg border border-gray-300 "
            "bg-gray-50 px-3 py-2 "
            "focus:border-blue-500 "
            "focus:ring-2 focus:ring-blue-500 "
            "transition"
        )

        for name, field in self.fields.items():

            if isinstance(
                field.widget,
                forms.CheckboxInput
            ):

                field.widget.attrs["class"] = (
                    "h-4 w-4 rounded"
                )

            elif isinstance(
                field.widget,
                forms.FileInput
            ):

                field.widget.attrs["class"] = (
                    "block w-full text-sm text-gray-700"
                )

            else:

                field.widget.attrs["class"] = (
                    base_class
                )