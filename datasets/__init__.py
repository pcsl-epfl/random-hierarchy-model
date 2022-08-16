from .hierarchical import *

def dataset_initialization(args):
    """
    Initialize train and test loaders for chosen dataset and transforms.
    :param args: parser arguments (see main.py)
    :return: trainloader, testloader, image size, number of classes.
    """

    nc = args.num_classes

    if args.seed_data != -1:
        torch.manual_seed(args.seed_data)

    if args.dataset == 'hier1':
        trainset = HierarchicalDataset(
            num_features=args.num_features,
            m=args.m,  # features multiplicity
            num_layers=args.num_layers,
            num_classes=nc,
            input_format=args.input_format,
            seed=args.seed_data,
            train=True,
            transform=None,
            testsize=args.pte
        )

        testset = HierarchicalDataset(
            num_features=args.num_features,
            m=args.m,  # features multiplicity
            num_layers=args.num_layers,
            num_classes=nc,
            input_format=args.input_format,
            seed=args.seed_data,
            train=False,
            transform=None,
            testsize=args.pte
        )

    else:
        raise ValueError('`dataset` argument is invalid!')

    input_dim = trainset[0][0].shape[-1]
    ch = trainset[0][0].shape[-2]

    if args.loss == 'hinge':
        # change to binary labels
        trainset.targets = 2 * (torch.as_tensor(trainset.targets) >= nc // 2) - 1
        testset.targets = 2 * (torch.as_tensor(testset.targets) >= nc // 2) - 1

    P = len(trainset)
    if args.ptr:
        # take random subset of training set
        perm = torch.randperm(P)
        trainset = torch.utils.data.Subset(trainset, perm[:args.ptr])

    trainloader = torch.utils.data.DataLoader(
        trainset, batch_size=args.batch_size, shuffle=True, num_workers=1)
    testloader = torch.utils.data.DataLoader(
        testset, batch_size=100, shuffle=False, num_workers=1)

    return trainloader, testloader, input_dim, ch
