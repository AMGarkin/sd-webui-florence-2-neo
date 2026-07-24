import launch

need_update = False

if launch.is_installed("transformers"):
    import transformers
    if transformers.__version__ < '4.41.2':
        need_update = True
else:
    need_update = True

if need_update:
    launch.run_pip("install transformers>=4.41.2", "transformers >= 4.41.2 for Florence")
