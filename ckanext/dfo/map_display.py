"""
This module does the following:
1. Exposes an endpoint (via map.connect in plugins.py) for the map display URL for a given resource
2. Check user permissions for the resource
3. If user is authorized, proceed with rendering the map display template
4. map display is done with HTML + OpenLayers. Each map tile request is authorized by ckanext-restricted
"""

import dfo_plugin_settings as settings
from ckan.logic import side_effect_free, get_action
from ckan.lib import base
from ckan.common import request
from ckan.common import c
import ckan.lib.helpers as h
import dfo_plugin_settings
from flask import send_file, jsonify, redirect
from subprocess import check_output, Popen
import traceback

render = base.render

logger = settings.setup_logger(__name__)


class MapDisplayController(base.BaseController):

    def map_display(self, dataset_id, resource_id):

        """ Make a context object.  Without this, we get an error from Flask:
        RuntimeError: Working outside of request context.
        The context object makes use of the global CKAN object 'c' which contains
        session info including the logged-in user.
        """
        context = {"user": c.user, "auth_user_obj": c.userobj}

        # request.params.get is only used for URL parameters after the ?
        # e.g. for gis-hub.ca/someurl?animal=dog we would use request.params.get('animal')
        # But here package_id, resource_id are part of the URL pattern, passed from map.connect in plugins.py

        # for k, v in request.params.iteritems():
        #     logger.info('%s: %s' % (k, v))
        # resource_id = request.params.get('resource_id')
        # dataset_id = request.params.get('dataset_id')
        logger.info('Map display requested: %s, %s' % (dataset_id, resource_id))

        """
        Need to do a few things before rendering the map. 
        1. Check if user is authorized for this resource
        2. Check that the resource_id actually exists in this dataset. This prevents users from 
        using a malformed URL to access a resource that they are not supposed to see. 
        3. Is this a raster or a vector layer? Use a different map template for each.
        4. Get the extent of the layer from geoserver. 
        Steps 3 and 4 have been handled by the Node.js middleware in mapserver until now. 
        5. Since we're going to change the map preview URLs, we need to add a piece of metadata to 
        every spatial resource with the Postgis table name / raster layer name. 
        e.g. resource 952a7f28-b73e-4bcc-a049-953db05cb396 in bops dataset has layer name 'bops_wcvi'
        This is already implicitly stored in the "map_preview_link" metadata field. 
        """

        # 1. Check if user is authorized for this resource
        # We can do a simpler version of this (compared to the way it works in ckanext-restricted)
        # Don't worry about this for now, just check if we can render the map display URL.

        # Get resource metadata
        import ckan.model as model
        from flask import abort as flask_abort
        resource = model.Resource.get(resource_id)
        if not resource:
            logger.warning('Resource %s not found!' % resource_id)
            flask_abort(401, 'Access denied')
        resource = resource.as_dict()
        layer_name = resource.get('layer_name')

        spatial_type = resource.get('spatial_type')
        if spatial_type not in ['raster', 'vector']:
            logger.warning('Map display requested for non-spatial resource: %s' % layer_name)
            return render(
                'map_display/resource_map_nopreview.html')


        data = {
            'dataset_id': dataset_id,
            'resource_id': resource_id,
            'spatial_type': spatial_type,
            'layer_name': layer_name
            }
        return render(
            'map_display/resource_map_display.html',
            extra_vars={'data': data})
            # dataset_id=dataset_id,
            # resource_id=resource_id)
            # context=context, extra_vars=extra_vars)



