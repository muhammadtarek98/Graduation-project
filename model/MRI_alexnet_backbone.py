import torch,torchvision
class MRI_alex(torch.nn.Module):
  def __init__(self, training=True):
    super().__init__()
    self.axial_net = torchvision.models.alexnet(pretrained=training)
    self.sagit_net = torchvision.models.alexnet(pretrained=training)
    self.coron_net = torchvision.models.alexnet(pretrained=training)

    self.gap_axial = torch.nn.AdaptiveAvgPool2d(1)
    self.gap_sagit = torch.nn.AdaptiveAvgPool2d(1)
    self.gap_coron = torch.nn.AdaptiveAvgPool2d(1)
    self.classifier = torch.nn.Linear(3*256, 1)

  def forward(self,vol_axial, vol_sagit, vol_coron):
    vol_axial = torch.squeeze(vol_axial, dim=0)
    vol_sagit = torch.squeeze(vol_sagit, dim=0)
    vol_coron = torch.squeeze(vol_coron, dim=0)

    vol_axial = self.axial_net.features(vol_axial)
    vol_sagit = self.sagit_net.features(vol_sagit)
    vol_coron = self.coron_net.features(vol_coron)

    vol_axial = self.gap_axial(vol_axial).view(vol_axial.size(0), -1)
    x = torch.max(vol_axial, 0, keepdim=True)[0]

    vol_sagit = self.gap_sagit(vol_sagit).view(vol_sagit.size(0), -1)
    y = torch.max(vol_sagit, 0, keepdim=True)[0]

    vol_coron = self.gap_coron(vol_coron).view(vol_coron.size(0), -1)
    z = torch.max(vol_coron, 0, keepdim=True)[0]

    w = torch.cat((x, y, z), 1)
    out = self.classifier(w)
    return out