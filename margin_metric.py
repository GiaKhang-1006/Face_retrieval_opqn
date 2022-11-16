import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import Parameter
import math


class OrthoPQ(nn.Module):

    def __init__(self, in_features, out_features, num_books, num_words, code_books, sc=30.0, m=0.50):
        super(OrthoPQ, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.num_books = num_books
        self.num_words = num_words
        self.len_word = int(self.in_features / self.num_books)
        self.s = sc
        self.m = m
        self.weight = Parameter(torch.FloatTensor(self.num_books, self.out_features, self.len_word))
        self.mlp = Parameter(torch.FloatTensor(self.num_books, self.len_word, self.num_words))
        self.codebooks = Parameter(code_books, requires_grad=False)
        nn.init.xavier_uniform_(self.weight)
        nn.init.xavier_uniform_(self.mlp)

    def forward(self, input, label):

        # ------------------------- cos(theta) & phi(theta) ---------------------------------
        x_m = torch.split(input, self.len_word, dim=1)
        cosine_xw = []
        # x = []
        xc_prod_softs = []
        weights_norm = F.normalize(self.weight, dim=2)
        for i in range(self.num_books):
            x_norm = F.normalize(x_m[i])
            cosine_xw.append(F.linear(x_norm, weights_norm[i]))
            xc_prod_softmax = F.softmax(x_m[i] @ self.mlp[i], dim=1)    # directly x_m @ mlp ?
            xc_prod_softs.append(xc_prod_softmax)
        xc_softmax = torch.stack(xc_prod_softs, dim=0)     # check: num_books, bs, num_words
        cosine_xww = torch.stack(cosine_xw, dim=0)

        # ------------------------- cos(sw)---------------------------------------------------
        s_m = torch.matmul(self.codebooks, torch.transpose(xc_softmax, 1, 2))   # construct s_m, shape of (num_books * len_word * bs), norm of convex comb. of codebooks smaller than 1

        cosine_sw = []
        for i in range(self.num_books):
            s_norm = F.normalize(s_m[i].t())
            cosine_sw.append(F.linear(s_norm, weights_norm[i]))
        cosine_sww = torch.stack(cosine_sw, dim=0)

        # ------------------------- OPQN-Loss.------------------------------------------------
        cos_theta1 = cosine_xww.clamp(-1, 1)
        cos_theta2 = cosine_sww.clamp(-1, 1)   # for numerical stability
        phi1 = cos_theta1 - self.m
        phi2 = cos_theta2 - self.m
        one_hot = torch.zeros(cosine_sww.shape[1:], device='cuda')
        one_hot.scatter_(1, label.view(-1, 1).long(), 1)
        one_hot_all = one_hot.repeat(self.num_books, 1, 1)

        output = (one_hot_all * phi1) + ((1.0 - one_hot_all) * cos_theta1)  # cosine similarity between x_i and w_i
        output2 = (one_hot_all * phi2) + ((1.0 - one_hot_all) * cos_theta2)  # cosine similarity between s_i and w_i

        output *= self.s
        output2 *= self.s
        # shape of output: M * bs * out_features

        ##############################################################################
        return torch.transpose(output, 0, 1), torch.transpose(output2, 0, 1), torch.transpose(xc_softmax, 0, 1)

