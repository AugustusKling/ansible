from ansible import utils
from ansible.runner.return_data import ReturnData
import ansible.utils.template as template
import pipes

class ActionModule(object):
    TRANSFERS_FILES = True

    def __init__(self, runner):
        self.runner = runner

    def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):
        ''' transfers SQL file so that postgresql_migration module know what to execute for its migrations. '''
        
        # load up options
        options = {}
        if complex_args:
            options.update(complex_args)
        options.update(utils.parse_kv(module_args))
        source = options.get('src', None)
        dest = options.get('dest', None)
        
        if source is None:
            results = dict(failed=True, msg="src is required")
            return ReturnData(conn=conn, result=results)
        
        source = template.template(self.runner.basedir, source, inject)
        if '_original_file' in inject:
            source = utils.path_dwim_relative(inject['_original_file'], 'files', source, self.runner.basedir)
        else:
            source = utils.path_dwim(self.runner.basedir, source)
        
        #tmp = self.runner._make_tmp_path(conn)
        tmp_src = tmp + 'source'
        
        conn.put_file(source, tmp_src)

        module_args_tmp = "%s src=%s" % (module_args, pipes.quote(tmp_src))
        return self.runner._execute_module(conn, tmp, module_name, module_args_tmp, inject=inject, complex_args=complex_args)