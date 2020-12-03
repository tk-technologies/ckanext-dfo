import dfo_plugin_settings as settings
from ckan.logic import side_effect_free, get_action
from ckan.lib import base
from ckan.common import request
import ckan.plugins as p
import dfo_plugin_settings
from flask import send_file, jsonify
from subprocess import check_output
import traceback


logger = settings.setup_logger(__name__)


@side_effect_free
def run_hnap(context, data_dict):
    resource_id = data_dict.get('resource_id')
    return generate_hnap_file(resource_id)


def generate_hnap_file(resource_id):
    logger.info('Running hub-geo-api for HNAP export of resource: %s' % resource_id)
    command_parts = [dfo_plugin_settings.hubapi_venv,
                     '/home/dfo/hub-geo-api/hnap_export.py',
                     '-r', resource_id]
    hnap_export_cmd = dfo_plugin_settings.run_command_as(command_parts)
    try:
        hnap_file = check_output(hnap_export_cmd)
        # Strip any excess characters such as trailing newline \n
        hnap_file = hnap_file.strip()
    except:
        logger.error(traceback.format_exc())
        return jsonify({'error': traceback.format_exc()})
    logger.info('Created HNAP XML file: %s' % hnap_file)
    return hnap_file
    # return jsonify({'hnap_file': hnap_file})
    # return send_file(hnap_file)


# Add to resource_read template:
# <li>{% link_for _('Manage'), named_route='resource.edit', id=pkg.name, resource_id=res.id, class_='btn btn-default', icon='wrench' %}</li>

class HNAPController(base.BaseController):

    def get_hnap(self):
        for k, v in request.params.iteritems():
            logger.info('%s: %s' % (k, v))
        resource_id = request.params.get('resource_id')
        dataset_id = request.params.get('dataset_id')
        logger.info('HNAP controller: %s %s' % (dataset_id, resource_id))
        hnap_file = generate_hnap_file(resource_id)
        return send_file(hnap_file)
        # return p.toolkit.render('docs/docs.html')

    # @side_effect_free
    # def get_hnap(self, context, data_dict):

    # @staticmethod
    # def get_hnap(dataset_id, resource_id):
    #     # return flask.send_file(filepath)
    #     logger.info('HNAP controller: %s %s' % (dataset_id, resource_id))
    #
    #     return p.toolkit.render('docs/docs.html')
