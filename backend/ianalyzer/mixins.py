from rest_framework import response, status, mixins


class DestroyWithPayloadMixin(mixins.DestroyModelMixin, object):
    def destroy(self, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        super().destroy(*args, **kwargs)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
