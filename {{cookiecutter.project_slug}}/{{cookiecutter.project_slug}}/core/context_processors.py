def webpack_dev_server(request):
    return {
        "webpack_dev_server": request.META.get("HTTP_X_WEBPACK_DEV_SERVER") == "yes"
    }
