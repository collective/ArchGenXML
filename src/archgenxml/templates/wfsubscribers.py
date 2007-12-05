<dtml-var "generator.generateModuleInfoHeader(package, name='wfsubscribers')">
<dtml-var "generator.getProtectedSection(parsed_module, 'module-header')">

<dtml-in "subscribers.keys()">
<dtml-let subscriber="subscribers[_['sequence-item']]">
def <dtml-var "subscriber['method']">(obj, event):
    """generated workflow subscriber."""
    # do only change the code section inside this function.
    if not event.transition or \
       event.transition.id != '<dtml-var "subscriber['payload']['transition']">':
        return
<dtml-var "generator.getProtectedSection(parsed_module, subscriber['method'], 1)">

</dtml-let>
</dtml-in>
<dtml-in "parsed_module.functions.keys()">
<dtml-let func="parsed_module.functions[_['sequence-item']]">
<dtml-if "func.name not in [subscribers[k]['method'] for k in subscribers.keys()]">
<dtml-var "func.src">
</dtml-if>
</dtml-let>
</dtml-in>

<dtml-var "generator.getProtectedSection(parsed_module, 'module-footer')">
