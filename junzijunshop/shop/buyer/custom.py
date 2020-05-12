from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        print(data)
        if data:
            data.update(author = 'pp',
                        time = 'xx'
                        )
        return super().render(data,accepted_media_type,renderer_context)

