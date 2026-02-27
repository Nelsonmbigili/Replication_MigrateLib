"""${name}.

Args:
% for p in params:
    ${p.argument}${' (' + p.annotation + '): ' + p.argument if p.annotation else ':'}
% endfor
% if return_type:
Returns:
    ${return_type}:
% endif
"""
