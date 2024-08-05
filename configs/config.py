import json


class BabsConf(dict):
  class ReprJSONEncoder(json.JSONEncoder):
    def default(self, obj):
      if isinstance(obj, BabsConf):
        return obj.to_dict()
      return super(BabsConf.ReprJSONEncoder, self).default(obj)

  def __init__(
      self,
      conf_type=None,
      **params
  ):
    # if the value is a dict, then we need to convert it to a BabsConf
    for k, v in params.items():
      if isinstance(v, dict):
        params[k] = BabsConf(**v)

    super(BabsConf, self).__init__(**params)

    if conf_type:
      self["conf_type"] = conf_type

  def __getattr__(self, item):
    try:
      return self[item]
    except KeyError as e:
      raise e

  def __getitem__(self, k):
    try:
      return super(BabsConf, self).__getitem__(k)
    except KeyError as e:
      raise e

  def to_dict(self):
    return dict(self)

  def __str__(self):
    return json.dumps(
      self.to_dict(),
      sort_keys=True,
      indent=2,
      cls=self.ReprJSONEncoder
    )
