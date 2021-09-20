import uuid


class UserIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # store random value in session

        session = request.session
        if "user_id" not in session:
            user_id = uuid.uuid4().hex
            request.session["user_id"] = user_id
        else:
            user_id = request.session["user_id"]

        response = self.get_response(request)

        return response
