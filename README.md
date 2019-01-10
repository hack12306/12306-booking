# 12306-booking
12306订票工具

## 订票流程

![订票流程](http://processon.com/chart_image/5c371415e4b08a7683a24cbe.png)

## 订票状态机

![订票状态机](http://processon.com/chart_image/5c371a11e4b0641c83d6eb3f.png)

## 订票使用说明

```sh
pip install 12306-booking -U --user;
123060-booking --train-date 2020-01-01 --train-name K571 --seat-types 硬卧 --from-station 北京 --to-station 麻城 --pay-channel 微信 --passengers 任正非,王石
```
> passengers如果有多个乘客，乘客之间用英文','分割。如果使用MacOS，使用虚拟安装`virtualenv venv; source venv/bin/activate; pip install 12306-booking -U`

## 赞助

如果该项目有帮助到你，请扫描二维码赞赏我们，你的鼓励是我们持续改进优化的动力。

<img src="https://share-static.oss-cn-hangzhou.aliyuncs.com/wx/%E5%BE%AE%E4%BF%A1%E8%B5%9E%E8%B5%8F.jpg"  width="50%" height="50%" />
