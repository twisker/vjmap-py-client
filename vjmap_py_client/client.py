import json
import requests
from typing import Optional, List, Tuple, Callable, Any
from .utils import file_md5, file_object_md5


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

    def _request(self, method: str, endpoint: str, as_json: bool = True, **kwargs):
        kwargs["params"] = kwargs.get("params", {})
        kwargs["params"]["token"] = self.access_token
        url = f"{self.base_url}{endpoint}" if endpoint.startswith('/') else f"{self.base_url}/{endpoint}"
        response = self.session.request(method, url, **kwargs)
        if response.status_code == 200:
            if as_json:
                return response.json()
            else:
                return response
        else:
            raise Exception(response.text)

    def _upload_file(self, endpoint: str, file_path: str, **kwargs):
        with open(file_path, 'rb') as file_object:
            res = self._upload_file_object(endpoint, file_object, **kwargs)
        return res

    def _upload_file_object(self, endpoint: str, file_object: Any, **kwargs):
        files = {'file': file_object}
        response = self._request('POST', endpoint, files=files, **kwargs)
        return response


class VjmapClient(VjmapClientBase):

    def upload_map(self, map_file_path: str, **kwargs):
        """
        Upload a map file to the Vjmap server.

        Parameters
        ----------
        map_file_path : str
            The path to the map file to be uploaded.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E4%B8%8A%E4%BC%A0%E5%9B%BE%E5%BD%A2
        """
        endpoint = '/map/uploads'
        return self._upload_file(endpoint, map_file_path, **kwargs)

    def upload_map_file_object(self, map_file_object: Any, **kwargs):
        """
        Upload a map file like object to the Vjmap server.

        Parameters
        ----------
        map_file_object : File like object
            The map file object to be uploaded. Its open() method shall be called.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E4%B8%8A%E4%BC%A0%E5%9B%BE%E5%BD%A2
        """
        endpoint = '/map/uploads'
        return self._upload_file_object(endpoint, map_file_object, **kwargs)

    def open_map(self, map_id: str, **kwargs):
        """
        Open a map from the Vjmap server.

        Parameters
        ----------
        map_id : str
            The ID of the map to be opened.
        params : dict
            Additional parameters to be passed to the server. see link below for details.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E5%88%9B%E5%BB%BA%E6%88%96%E6%89%93%E5%BC%80%E5%9B%BE%E5%BD%A2
        """
        endpoint = f'/map/openmap/{map_id}'
        return self._request('GET', endpoint, **kwargs)

    def update_map(self, map_id: str, entities: list, **kwargs):
        """
        Update a map from the Vjmap server.

        Parameters
        ----------
        map_id : str
            The ID of the map to be updated.
        entities : list
            The list of entities to be updated.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E6%9B%B4%E6%96%B0%E5%9B%BE%E5%BD%A2
        """
        endpoint = f'/map/updatemap/{map_id}'
        file_data = json.dumps({"entities": entities})
        json_data = {
            "fileid": file_data
        }
        return self._request('POST', endpoint, json=json_data, **kwargs)

    def map_file_uploaded(self, map_file_path: str, **kwargs):
        """
        Check if a map file has been uploaded to the Vjmap server.

        Parameters
        ----------
        map_file_path : str
            The path to the map file to be checked.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E6%A3%80%E6%9F%A5%E6%96%87%E4%BB%B6%E6%98%AF%E5%90%A6%E4%B8%8A%E4%BC%A0%E8%BF%87
        """
        endpoint = '/map/mapfile'
        return self._request("GET", endpoint, params={"md5": file_md5(map_file_path)}, **kwargs)

    def map_file_object_uploaded(self, map_file_object: Any, **kwargs):
        """
        Check if a map file like object has been uploaded to the Vjmap server.

        Parameters
        ----------
        map_file_object : File like object
            The map file object to be uploaded. Its open() method shall be called.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E6%A3%80%E6%9F%A5%E6%96%87%E4%BB%B6%E6%98%AF%E5%90%A6%E4%B8%8A%E4%BC%A0%E8%BF%87
        """
        endpoint = '/map/mapfile'
        return self._request("GET", endpoint, params={"md5": file_object_md5(map_file_object)}, **kwargs)

    def get_map_tile(self, map_id: str, version: str, stylename: str, zoom: int, x: int, y: int, fileid: str, as_mvt: bool = False, **kwargs):
        """
        Get a map tile from the Vjmap server.

        Parameters
        ----------
        map_id : str
            The ID of the map to get the tile from.
        version : str
            The version of the map to get the tile from.
        stylename : str
            The name of the style to get the tile from.
        zoom : int
            The zoom level of the tile to get.
        x : int
            The x coordinate of the tile to get.
        y : int
            The y coordinate of the tile to get.
        fileid : str
            The ID of the file to get the tile from.
        as_mvt : bool
            Whether to return the tile as a MVT tile.

        Returns
        -------
        response : HttpResponse
            The response from the server.

        :link: https://vjmap.com/guide/restinterface.html#%E6%A0%85%E6%A0%BC%E7%93%A6%E7%89%87%E5%9C%B0%E5%9D%80
        :link: https://vjmap.com/guide/restinterface.html#%E7%9F%A2%E9%87%8F%E7%93%A6%E7%89%87%E5%9C%B0%E5%9D%80
        """
        endpoint = f'/map/tile/{map_id}/{version}/{stylename}/{zoom}/{x}/{y}'
        if as_mvt:
            endpoint += '.mvt'
        return self._request('GET', endpoint, as_json=False, params={"tag": fileid}, **kwargs)

    def list_maps(self, map_id: str, version: str, **kwargs):
        """
        List maps from the Vjmap server.

        Parameters
        ----------
        map_id : str
            The ID of the map to list.
        version : str
            The version of the map to list.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E8%8E%B7%E5%8F%96%E5%9C%B0%E5%9B%BE%E5%88%97%E8%A1%A8
        """
        endpoint = f'/map/cmd/listmaps/{map_id}/{version}'
        return self._request('GET', endpoint, **kwargs)

    def query_features(self, map_id: str, version: str, parameters: PointQueryParameter|RectQueryParameter|ExprQueryParameter|ConditionQueryParameter, **kwargs):
        """
        Query features from the Vjmap server.

        Parameters
        ----------
        map_id : str
            The ID of the map to query.
        version : str
            The version of the map to query.
        parameters : PointQueryParameter|RectQueryParameter|ExprQueryParameter|ConditionQueryParameter
            The parameters to be used in the query.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E6%9F%A5%E8%AF%A2%E5%AE%9E%E4%BD%93
        """
        endpoint = f'/map/cmd/queryFeatures/{map_id}/{version}'
        return self._request('POST', endpoint, json=parameters.to_dict(), **kwargs)

    def get_data_bounds(self, map_id: str, version: str, **kwargs):
        """
        Get data bounds from the Vjmap server.

        Parameters
        ----------
        map_id : str
            The ID of the map to get data bounds from.
        version : str
            The version of the map to get data bounds from.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E8%8E%B7%E5%8F%96%E5%9B%BE%E5%BD%A2%E4%B8%AD%E6%9C%89%E6%95%B0%E6%8D%AE%E7%9A%84%E8%8C%83%E5%9B%B4%E5%8C%BA%E5%9F%9F
        """
        endpoint = f'/map/cmd/getDataBounds/{map_id}/{version}'
        return self._request('GET', endpoint, **kwargs)

    def get_thumbnail(self, map_id: str, version: str, width: int = 100, height: int = 100, dark_theme: bool = False, **kwargs):
        """
        Get a thumbnail from the Vjmap server.

        Parameters
        ----------
        map_id : str
            The ID of the map to get the thumbnail from.
        version : str
            The version of the map to get the thumbnail from.
        width : int
            The width of the thumbnail.
        height : int
            The height of the thumbnail.
        dark_theme : bool
            Whether to use a dark theme for the thumbnail.

        Returns
        -------
        response : HttpResponse
            The response from the server.

        :link: https://vjmap.com/guide/restinterface.html#%E8%8E%B7%E5%8F%96%E5%9B%BE%E7%9A%84%E7%BC%A9%E7%95%A5%E5%9B%BE
        """
        endpoint = f'/map/cmd/thumbnail/{map_id}/{version}'
        return self._request('GET', endpoint, as_json=False, params={"width": width, "height": height, "darkTheme": dark_theme}, **kwargs)

    def close_map(self, map_id: str, version: str, **kwargs):
        """
        Close a map from the Vjmap server.

        Parameters
        ----------
        map_id : str
            The ID of the map to close.
        version : str
            The version of the map to close.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E4%B8%BB%E5%8A%A8%E5%85%B3%E9%97%AD%E6%89%93%E5%BC%80%E7%9A%84%E5%9C%B0%E5%9B%BE
        """
        endpoint = f'/map/cmd/closemap/{map_id}/{version}'
        return self._request('POST', endpoint, **kwargs)

    def get_metadata(self, map_id: str, version: str, geom: bool = False, **kwargs):
        """
        Get metadata from the Vjmap server.

        Parameters
        ----------
        map_id : str
            The ID of the map to get metadata from.
        version : str
            The version of the map to get metadata from.
        geom : bool
            Whether to include the geometry in the response.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E8%8E%B7%E5%8F%96%E5%9C%B0%E5%9B%BE%E5%85%83%E6%95%B0%E6%8D%AE
        """
        endpoint = f'/map/cmd/metadata/{map_id}/{version}'
        return self._request('GET', endpoint, params={"geom": geom}, **kwargs)

    def update_metadata(self, map_id: str, version: str, metadata: dict, **kwargs):
        """
        Update metadata in the Vjmap server.

        Parameters
        ----------
        map_id : str
            The ID of the map to update metadata in.
        version : str
            The version of the map to update metadata in.
        metadata : dict
            The metadata to update.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E4%BF%AE%E6%94%B9%E5%9C%B0%E5%9B%BE%E5%85%83%E6%95%B0%E6%8D%AE
        """
        endpoint = f'/map/cmd/updateMetadata/{map_id}/{version}'
        return self._request('POST', endpoint, json=metadata, **kwargs)

    def switch_layers(self, map_id: str, version: str, visible_layers: list, dark_mode: bool = False, **kwargs):
        """
        Switch layers in the Vjmap server.

        Parameters
        ----------
        map_id : str
            The ID of the map to switch layers in.
        version : str
            The version of the map to switch layers in.
        visible_layers : list
            The list of layers to switch to visible.
        dark_mode : bool
            Whether to switch to dark mode.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E5%88%87%E6%8D%A2%E5%9B%BE%E5%B1%82
        """
        endpoint = f'/map/cmd/switchlayers/{map_id}/{version}'
        return self._request('POST', endpoint, json={"visibleLayers": visible_layers, "darkMode": dark_mode}, **kwargs)

    def create_map_style(self, map_id: str, version: str, style: dict, **kwargs):
        """
        Create a map style in the Vjmap server.

        Parameters
        ----------
        map_id : str
            The ID of the map to create a map style in.
        version : str
            The version of the map to create a map style in.
        style : dict
            The style to create.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E8%8E%B7%E5%8F%96%E6%A0%B7%E5%BC%8F%E5%9B%BE%E5%B1%82%E5%90%8D
        """
        endpoint = f'/map/cmd/createMapStyle/{map_id}/{version}'
        return self._request('POST', endpoint, json=style, **kwargs)

    def delete_map(self, map_id: str, version: str, retain_version_count: str = 0, **kwargs):
        """
        Delete a map in the Vjmap server.

        Parameters
        ----------
        map_id : str
            The ID of the map to delete.
        version : str
            The version of the map to delete.
        retain_version_count : int, optional, default: 0
            The number of versions to retain.

        Returns
        -------
        response : dict
            The response from the server as a dict.

        :link: https://vjmap.com/guide/restinterface.html#%E5%88%A0%E9%99%A4%E5%9B%BE
        """
        endpoint = f'/map/cmd/deletemap/{map_id}/{version}'
        return self._request('POST', endpoint, json={"retainVersionMaxCount": retain_version_count}, **kwargs)
