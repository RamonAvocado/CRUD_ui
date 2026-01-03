import types
import inspect
from typing import Callable
from fastapi import APIRouter, Body, Query

class Crud:
    def __init__(self, cls, operations = {"Create", "Read", "Update", "Delete"}):
        self.cls = cls
        self.operations: set[str] = operations

        router_prefix = self._map_naming_convention("/"+cls.__name__)
        self.router = APIRouter(prefix=router_prefix, tags=[router_prefix])

        for operation in operations:
            endpoint = self._map_operation_to_endpoint(operation)
            method = self._function_creator(endpoint=endpoint, operation=operation, cls=self.cls)

            self.router.add_api_route(
                f"/{operation.lower()}",
                method,
                methods=self._map_operation_to_endpoint(operation)
            )

    def _map_naming_convention(self, name: str, *, convention = "kebab_case"):
        # TODO: THIS FUNCTION IS NOT IMPLEMENTED
        return name.lower()

    def _map_operation_to_endpoint_function(self, op):
        mapping = {
            "Create": self.router.post,
            "Read": self.router.get,
            "Update": self.router.put,
            "Delete": self.router.delete,
        }
        return mapping[op]

    def _map_operation_to_endpoint(self, op:str):
        mapping = {
            "Create": {"POST"},
            "Read": {"GET"},
            "Update": {"PUT"},
            "Delete": {"DELETE"},
        }
        return mapping[op]

    def _function_creator(self, endpoint: set, operation, cls):
        def handler() -> Callable:
            print(endpoint)

            if "POST" in endpoint:
                return self._create_endpoint(cls, operation)
            elif "GET" in endpoint:
                return self._read_endpoint(cls, operation)
            elif "PUT" in endpoint:
                return self._update_endpoint(cls, operation)
            elif "DELETE" in endpoint:
                return self._delete_endpoint(cls, operation)
            else:
                return self._read_endpoint(cls, operation)

        return handler()

    def _extracting_annotations_from_cls(self, cls:type):
        annotations = cls.__annotations__
        if not annotations:
            # When defining the class with __init__
            signature_parameters = inspect.signature(cls.__init__).parameters
            annotations = signature_parameters.copy()
            annotations.pop("self")

        return annotations

    def _create_endpoint(self, cls, function_name) -> Callable:
        return self._default_endpoint(cls, function_name, Body)

    def _read_endpoint(self, cls, function_name) -> Callable:
        return self._default_endpoint(cls, function_name, Query)

    def _update_endpoint(self, cls, function_name):
        return self._default_endpoint(cls, function_name, Body)

    def _delete_endpoint(self, id: int, function_name):
        return self._create_function()

    def _default_endpoint(self, cls: type, function_name:str,  fastapi_callable: Callable):
        annotations = self._extracting_annotations_from_cls(cls)

        parameters = []
        env = {}
        for p, meta in annotations.items():
            item_type = meta.annotation
            env[f"__t_{p}"] = item_type
            env[f"__d_{p}"] = fastapi_callable(...)
            parameters.append(f"{p}:__t_{p} = __d_{p}")

        sig =", ".join(parameters)
        src = self._create_function_str(name=function_name, sig=sig) 
        ns = {}
        exec(src, env, ns)
        print(ns)
        return ns[function_name]

    def _create_code(self, a):
        print("HELLO")
        return {"Test"}

    def _create_function(self):
        func = types.FunctionType(
            self._create_code.__code__,
            {"__builtins__": __builtins__},
            # name="NEWEIRD",
            # argdefs=(),
            # closure=None
        )
        return func

    def _create_function_str(self, name, sig):
        return f"""
def {name}({sig}):
    return {"Test"}
        """


    def get_router(self):
        return self.router

    
