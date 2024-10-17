import json
import requests
from typing import Optional, List, Tuple, Callable, Any
from .utils import file_md5


# 定义查询实体参数基类
class QueryParameterBase:
    def __init__(
            self,
            zoom: Optional[int] = 1,
            mapid: Optional[str] = None,
            version: Optional[str] = None,
            layer: Optional[str] = None,
            limit: Optional[int] = None,
            fields: Optional[str] = "",
            geom: Optional[bool] = None,
            simplifyTolerance: Optional[bool] = None,
            useCache: Optional[bool] = False,
            toMapCoordinate: Optional[bool] = None
    ):
        self.zoom = zoom
        self.mapid = mapid
        self.version = version
        self.layername = layer
        self.maxReturnCount = limit
        self.fields = fields
        self.geom = geom
        self.simplifyTolerance = simplifyTolerance
        self.useCache = useCache
        self.toMapCoordinate = toMapCoordinate

    def to_dict(self):
        return dict((k, v) for k, v in self.__dict__.items() if v is not None)


# 点查询实体参数类
class PointQueryParameter(QueryParameterBase):
    def __init__(
            self,
            x: float,
            y: float,
            pixelsize: Optional[int] = 5,
            condition: Optional[str] = None,
            maxGeomBytesSize: Optional[int] = None,
            pixelToGeoLength: Optional[float] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.querytype = "point"
        self.x = x
        self.y = y
        self.pixelsize = pixelsize
        self.condition = condition
        self.maxGeomBytesSize = maxGeomBytesSize
        self.pixelToGeoLength = pixelToGeoLength


# 矩形查询实体参数类
class RectQueryParameter(QueryParameterBase):
    def __init__(
            self,
            x1: Optional[float] = None,
            y1: Optional[float] = None,
            x2: Optional[float] = None,
            y2: Optional[float] = None,
            condition: Optional[str] = None,
            maxGeomBytesSize: Optional[int] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.querytype = "rect"
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.condition = condition
        self.maxGeomBytesSize = maxGeomBytesSize


# 表达式查询实体参数类
class ExprQueryParameter(QueryParameterBase):
    def __init__(
            self,
            expr: str,
            beginpos: Optional[int] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.querytype = "expresion"
        self.expr = expr
        self.beginpos = beginpos


# 条件查询实体参数类
class ConditionQueryParameter(QueryParameterBase):
    def __init__(
            self,
            condition: str,
            bounds: Optional[Tuple[float, float, float, float]] = None,
            beginpos: Optional[int] = None,
            includegeom: Optional[bool] = None,
            realgeom: Optional[bool] = None,
            isContains: Optional[bool] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.querytype = "condition"
        self.condition = condition
        self.bounds = json.dumps(bounds) if bounds else ""
        self.beginpos = beginpos
        self.includegeom = includegeom
        self.realgeom = realgeom
        self.isContains = isContains


class VjmapClientBase(object):

    def __init__(self, access_token, base_url='https://vjmap.com/server/api/v1'):
        self.access_token = access_token
        self.base_url = base_url[:-1] if base_url.endswith('/') else base_url
        self.session = requests.Session()
        self.session.headers.update({"Token": access_token})

    def _request(self, method: str, endpoint: str, **kwargs):
        if method.upper() == "GET":
            kwargs["params"] = kwargs.get("params", {})
            kwargs["params"]["token"] = self.access_token
        url = f"{self.base_url}{endpoint}" if endpoint.startswith('/') else f"{self.base_url}/{endpoint}"
        response = self.session.request(method, url, **kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.text)

    def _upload_file(self, endpoint: str, file_path: str, **kwargs):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = self._request('POST', endpoint, files=files, **kwargs)
            return response


class VjmapClient(VjmapClientBase):

    def upload_map(self, map_file_path: str, **kwargs):
        endpoint = '/map/uploads'
        return self._upload_file(endpoint, map_file_path, **kwargs)

    def open_map(self, map_id: str, **kwargs):
        endpoint = f'/map/openmap/{map_id}'
        return self._request('GET', endpoint, **kwargs)

    def update_map(self, map_id: str, entities: list, **kwargs):
        endpoint = f'/map/updatemap/{map_id}'
        file_data = json.dumps({"entities": entities})
        json_data = {
            "fileid": file_data
        }
        return self._request('POST', endpoint, json=json_data, **kwargs)

    def map_file_uploaded(self, map_file_path: str, **kwargs):
        endpoint = '/map/mapfile'
        return self._request("GET", endpoint, params={"md5": file_md5(map_file_path)}, **kwargs)

    def get_map_tile(self, map_id: str, version: str, stylename: str, zoom: int, x: int, y: int, fileid: str, as_mvt: bool = False, **kwargs):
        endpoint = f'/map/tile/{map_id}/{version}/{stylename}/{zoom}/{x}/{y}'
        if as_mvt:
            endpoint += '.mvt'
        return self._request('GET', endpoint, params={"tag": fileid}, **kwargs)

    def list_maps(self, map_id: str, version: str, **kwargs):
        endpoint = f'/map/cmd/listmaps/{map_id}/{version}'
        return self._request('GET', endpoint, **kwargs)

    def query_features(self, map_id: str, version: str, parameters: PointQueryParameter|RectQueryParameter|ExprQueryParameter|ConditionQueryParameter, **kwargs):
        endpoint = f'/map/cmd/queryFeatures/{map_id}/{version}'
        return self._request('POST', endpoint, json=parameters.to_dict(), **kwargs)

    def get_data_bounds(self, map_id: str, version: str, **kwargs):
        endpoint = f'/map/cmd/getDataBounds/{map_id}/{version}'
        return self._request('GET', endpoint, **kwargs)

    def get_thumbnail(self, map_id: str, version: str, **kwargs):
        endpoint = f'/map/cmd/thumbnail/{map_id}/{version}'
        return self._request('GET', endpoint, **kwargs)
