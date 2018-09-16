from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.ext.declarative import  declarative_base
from sqlalchemy.orm import sessionmaker
import click
from prettytable import PrettyTable
import os


engine=create_engine('sqlite:///data.db')

Session=sessionmaker(bind=engine)

session=Session()

Base=declarative_base()


class Password(Base):
    __tablename__='password'

    id=Column(Integer,primary_key=True,autoincrement=True)
    desc = Column(String(100), doc='记录描述')
    uname=Column(String(50))
    passwd=Column(String(50))
    extra=Column(String(100),doc='额外信息,例如网址')

Base.metadata.create_all(engine) #创建表


@click.group()
def cli():
    pass


@cli.command()
@click.option('-d','--desc',default='',help='描述')
@click.option('-u','--uname',default='',help='用户名')
@click.option('-p','--passwd',default='',help='密码')
@click.option('-e','--extra',default='',help='额外信息')
def add(desc,uname,passwd,extra):
    item=Password(desc=desc,uname=uname,passwd=passwd,extra=extra)
    session.add(item)
    session.commit()
    print('ok')


@cli.command()
@click.option('-s','--search',default='',help='查找记录')
def query(search):
    tb=PrettyTable(['id','desc','username','password','extra'])
    q=session.query(Password)
    if search:
        for item in q.filter(Password.desc.like('%'+search+'%')).all():
            tb.add_row([item.id, item.desc, item.uname, item.passwd, item.extra])
    else:
        for item in q.all():
            tb.add_row([item.id,item.desc,item.uname,item.passwd,item.extra])
    print(tb)


@cli.command()
@click.option('-i','--id',type=int,default=0,help="记录id")
def delete(id):
    if id>0:
        session.delete(session.query(Password).filter(Password.id==id).first())
        session.commit()
        print('ok')
    else:
        print('未知id')


@cli.command()
@click.option('-i','--id',type=int,default=0,help="记录id")
@click.option('-d','--desc',default='',help='描述')
@click.option('-u','--uname',default='',help='用户名')
@click.option('-p','--passwd',default='',help='密码')
@click.option('-e','--extra',default='',help='额外信息')
def update(id,desc,uname,passwd,extra):
    if id>0:
        item=session.query(Password).filter(Password.id==id).first()
        if desc:
            item.desc = desc
        if uname:
            item.uname = uname
        if passwd:
            item.passwd = passwd
        if extra:
            item.extra = extra
        session.commit()
        print('ok')
    else:
        print('未知id')


if __name__ == '__main__':
    cli()


