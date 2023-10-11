from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


from requestdataapp.forms import UserBioForm, UploadFileForm


def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get("a", "")
    b = request.GET.get("b", "")
    result = a + b
    context = {
        "a": a,
        "b": b,
        "result": result,
    }

    return render(request, 'requestdataapp/request-query-params.html', context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        "form": UserBioForm(),
    }
    return render(request, 'requestdataapp/user-bio-form.html', context=context)


def handle_file_upload(request: HttpRequest, message: str = "", file_size: int = 0) -> HttpResponse:

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            myfile = form.cleaned_data["file"]
            file_for_storage = FileSystemStorage()
            file_size = File(myfile).size

            if file_size <= 10485760:
               filename = file_for_storage.save(myfile.name, myfile)
               message = "File saved successfully"
               print("saved file", filename)
            else:
               message = "Unable to upload file more than 10 (Mb)"
    else:
        form = UploadFileForm()

    context = {
        "message": message,
        "file_size": file_size,
        "form": form,
    }
    return render(request, 'requestdataapp/file-upload.html', context=context)
