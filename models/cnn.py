import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBlockNT(nn.Module):
    """
        Convolutional block with NTK initialization
    """

    def __init__(self, input_ch, h, filter_size, stride, pbc, batch_norm=False):

        super().__init__()
        self.w = nn.Parameter(
            torch.randn(h, input_ch, filter_size)
        )
        self.b = nn.Parameter(torch.randn(h))
        self.stride = stride
        self.pbc = pbc
        self.batch_norm = batch_norm
        if batch_norm:
            self.bn = nn.BatchNorm1d(num_features=h)

    def forward(self, x):

        if self.pbc:
            pool_size = (self.w.size(-1) - 1) // 2
            x = F.pad(x, (pool_size,
                          pool_size), mode='circular')
        h = self.w[0].numel()
        x = F.conv1d(x, self.w / h ** .5,
                     bias=self.b * 0.1, # / h ** .5,
                     stride=self.stride).relu()
        if self.batch_norm:
            x = self.bn(x)
        return x

class ConvBlockSD(nn.Module):
    """
    Convolutional block with standard torch initialization
    """

    def __init__(self, input_ch, h, filter_size, stride, pbc, bias=True, batch_norm=False):

        super().__init__()
        self.conv = nn.Conv1d(
            in_channels=input_ch,
            out_channels=h,
            kernel_size=filter_size,
            stride=stride,
            bias=bias)
        if batch_norm:
            self.bn = nn.BatchNorm1d(num_features=h)
        self.batch_norm = batch_norm
        self.filter_size = filter_size
        self.pbc = pbc

    def forward(self, x):

        if self.pbc:
            pool_size = int((self.filter_size - 1) / 2.)
            x = F.pad(x, (pool_size, pool_size), mode='circular')
        x = self.conv(x)
        x = x.relu()
        if self.batch_norm:
            x = self.bn(x)

        return x

class ConvNetGAPMF(nn.Module):
    """
    Convolutional neural network with MF initialization and global average
    pooling
    """

    def __init__(
            self, n_blocks, input_ch, h,
            filter_size, stride, pbc, out_dim, batch_norm):

        super().__init__()
        self.conv = nn.Sequential(ConvBlockNT(input_ch, h, filter_size, stride, pbc, batch_norm=batch_norm),
                                  *[ConvBlockNT(h, h, filter_size, stride, pbc, batch_norm=batch_norm)
                                      for _ in range(n_blocks-1)]
                                  )
        self.beta = nn.Parameter(torch.randn(h, out_dim))

    def forward(self, x):

        y = self.conv(x)
        y = y.mean(dim=[-1])
        y = y @ self.beta / self.beta.size(0)

        return y.squeeze()
