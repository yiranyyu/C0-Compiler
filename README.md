# C0-Compiler

## How to start

For Linux or MacOS with python3:

```sh
# setup
git clone https://github.com/yiranyyu/C0-Compiler
cd C0-Compiler

# get assemble output
./src/cc0.py -s <input-file> -o <output-file>

# get binary output
./src/cc0.py -s <input-file> -o <output-file>

# for more options
./src/cc0.py -h
```

For Windows with python3:

```sh
# setup
git clone https://github.com/yiranyyu/C0-Compiler
cd C0-Compiler

# get assemble output
python ./src/cc0.py -s <input-file> -o <output-file>

# get binary output
python ./src/cc0.py -s <input-file> -o <output-file>

# for more options
python ./src/cc0.py -h
```

## 完成度



| 完成的部分                        | 说明    |
| --------------------------------- | ------- |
| **c0 基础语法**                   |         |
| c0 扩展 —— 注释                   | 系数 1  |
| c0 扩展 —— 作用域与生命周期       | 系数 3  |
| c0 扩展 —— 字面量+类型转换+char   | 系数 9  |
| c0 扩展 —— 字面量+类型转换+double | 系数 10 |

### 未定义行为



| 未定义行为                               | 处理方式                                        |
| ---------------------------------------- | ----------------------------------------------- |
| 使用过大的字面量                         | 引发编译错误                                    |
| 使用未初始化的 const 变量                | 不处理                                          |
| 返回类型非 void 的函数中无返回语句的分支 | 返回 0 (int) 或者 0.0 (double) 或者 \x00 (char) |
| 返回类型为 void 的函数中无返回语句的分支 | 执行完分支中最后一条可达的语句后返回            |
| scan 和 print 的 IO 问题                 | 不处理                                          |
| 使用当前或者外层作用域之后会声明的变量   | 引发编译错误                                    |
|                                          |                                                 |

