from . import target


def remote_call(func):
    def callback_template(app_instance, target: target.Target, *args, **kwargs):
        print(app_instance, target, args, kwargs)

        func_name = f"{app_instance.__class__.__name__}:{func.__name__}"
        call_id = target.dispatch_call(func_name=func_name, kwargs=kwargs)
        result = target.wait_result(call_id, timeout=500)
        return result

    class Handler:

        def __init__(self) -> None:
            self.instance = None
            self.callback = func

        def __call__(self, target: target.Target, *args, **kwargs):
            return callback_template(self.instance, target, *args, **kwargs)

        def exec(self, instance, *args, **kwargs):
            return self.callback(instance, *args, **kwargs)

        def __get__(self, obj, _obj_type):
            self.instance = obj
            return self

    return Handler()
