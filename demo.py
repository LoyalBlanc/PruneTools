import os

import torch
import torch.nn as nn

import modules.abstract_network as an
import modules.basic_module as bm


class DemoNet(an.AbstractNetwork):
    def __init__(self):
        an.AbstractNetwork.__init__(self)

        self.conv4 = bm.Conv2d(32, 16, 3, padding=1)
        self.activate = nn.ReLU()
        self.bn2 = bm.BatchNorm2d(32)
        self.conv2 = bm.Conv2d(16, 32, 3, padding=1)
        self.conv3 = bm.Conv2d(32, 32, 3, padding=1)
        self.bn1 = bm.BatchNorm2d(16)
        self.max_pooling = nn.AdaptiveMaxPool2d(1)
        self.conv5 = bm.Conv2d(16, 10, 3, padding=1)
        self.bn3 = bm.BatchNorm2d(32)
        self.conv1 = bm.Conv2d(1, 16, 3, padding=1)
        self.bn4 = bm.BatchNorm2d(16)

        self.network_analysis(1)

    def forward(self, input_tensor):
        x1 = self.activate(self.bn1(self.conv1(input_tensor)))
        x2 = self.activate(self.bn2(self.conv2(x1)))
        x3 = self.activate(self.bn3(self.conv3(x2)))
        x4 = self.activate(self.bn4(self.conv4(x3 + x2)))
        x5 = self.conv5(x4 + x1)
        return self.max_pooling(x5).squeeze_()


if __name__ == "__main__":
    import method.abstract_method as pruning_methods
    import utils.utils_mnist as utils_mnist

    torch.manual_seed(229)
    os.environ["CUDA_VISIBLE_DEVICES"] = "2"

    """
    demo_flag:
    0: preparing for test
    1: one-shot pruning with 20 epochs fine-tuning
    2: 20 epochs iterative pruning
    3: 20 epochs automatic pruning
    """
    demo_flag = 2
    demo_net = DemoNet()
    pruning_tool = pruning_methods.PruningTool(
        input_channel=1)
    training_dataset = utils_mnist.get_train_loader(1000)

    if demo_flag == 0:
        utils_mnist.train_model(demo_net, epochs=1000, batch_size=1000, regular=False)
        utils_mnist.valid_model(demo_net, batch_size=1000)  # 0 / FLOPs 305152
        utils_mnist.save_param(demo_net, "demo_param.pkl")
    elif demo_flag == 1:
        utils_mnist.load_param(demo_net, "demo_param.pkl")
        pruning_tool.one_shot_pruning(demo_net)
        utils_mnist.valid_model(demo_net, batch_size=1000)  # 0 / FLOPs
        utils_mnist.train_model(demo_net, epochs=20, batch_size=1000, regular=False)
        utils_mnist.valid_model(demo_net, batch_size=1000)  # 0 / FLOPs
    elif demo_flag == 2:
        utils_mnist.load_param(demo_net, "demo_param.pkl")
        pruning_tool.iterative_pruning(demo_net, training_dataset, nn.CrossEntropyLoss())
        utils_mnist.valid_model(demo_net, batch_size=1000)  # 0 / FLOPs
    elif demo_flag == 3:
        utils_mnist.load_param(demo_net, "demo_param.pkl")
        pruning_tool.automatic_pruning(demo_net, training_dataset, nn.CrossEntropyLoss())
        utils_mnist.valid_model(demo_net, batch_size=1000)  # 0 / FLOPs
