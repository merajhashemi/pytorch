"""Default set of benchmarks."""

from core.api import GroupedModules, GroupedStmts
from core.types import FlatIntermediateDefinition
from core.utils import flatten, parse_stmts
from definitions.setup import Setup


BENCHMARKS: FlatIntermediateDefinition = flatten({
    "Empty": {
        "no allocation": GroupedStmts(
            r"torch.empty(())",
            r"torch::empty({0});",
        ),
    },

    "Pointwise": {
        "Math": {
            "add": {
                "Tensor-Scalar": GroupedStmts(
                    r"x += 1.0",
                    r"x += 1.0;",
                    setup=Setup.GENERIC.value,
                ),
            },
        },
    },

    "nn Modules": {
        "Linear": GroupedModules(
            "model = torch.nn.Linear(4, 2)",
            "auto model = torch::nn::Linear(4, 2);",
            setup=Setup.TRIVIAL_4D.value,
            signature="f(x) -> y",
            torchscript=True,
        ),
    },

    "training": {
        "simple": GroupedStmts(
            *parse_stmts(r"""
                Python                                   | C++
                ---------------------------------------- | ----------------------------------------
                a0 = torch.nn.functional.relu(x * w0)    | auto a0 = torch::nn::functional::relu(x * w0);
                y = a0 * w1                              | auto y = a0 * w1;
            """),
            Setup.TRAINING.value,
            num_threads=(1, 2),
            signature=r"f(x, w0, w1) -> y",
            torchscript=True,
            autograd=True,
        ),

        "ensemble": GroupedStmts(
            *parse_stmts(r"""
                Python                                   | C++
                ---------------------------------------- | ----------------------------------------
                a0 = torch.nn.functional.gelu(x * w0)    | auto a0 = torch::nn::functional::gelu(x * w0);
                a1 = torch.nn.functional.prelu(y, w1)    | auto a1 = torch::nn::functional::prelu(y, w1);
                z = torch.nn.functional.normalize(       | auto z = torch::nn::functional::normalize(
                    torch.cat([a0, a1]),                 |     torch::cat({a0, a1}),
                    p=2.0, dim=0,                        |     torch::nn::functional::NormalizeFuncOptions().p(2).dim(0)
                ).dot(w2)                                | ).dot(w2);
            """),
            Setup.TRAINING.value,
            num_threads=(1, 2),
            signature=r"f(x, y, w0, w1, w2) -> z",
            torchscript=True,
            autograd=True,
        ),
    },
})
