REST and MQTT for IFTTT
=======================

## What's IFTTT?
IFTTT is a service that enables users to **connect different web applications** (e.g., Facebook, Evernote, Weather, Dropbox, etc.) together through simple conditional statements known as "Recipes". [Source: Wikipedia]

A recipe is a (trigger, action) pair. However, IFTTT doesn't support fully custom actions. However, it does support publishing to any Wordpress blog. This app emulates Wordpress's XML-RPC API so that you can send a `GET`/`POST`/`PUT` REST request, or publish a MQTT message, all by choosing the "create post" action in IFTTT.

## Install
Simply clone this repository and upload as a Heroku app, or host it however you want.

For local testing, you can use `flaskrun.py`. If desired, use a `virtualenv`, and install all the packages in `requirements.txt`.

## Usage
Set the **title** and **body** of the post. Everything else is ignored.
####Examples:
* title = `GET http://httpbin.org/get?some=stuff&here`
* title = `POST http://example.com/something`, body = `whatever data you want to post` (similarly for `PUT`)
* title = `MQTT-PUB mqtt://iot.eclipse.org/topic/name/goes/here?qos=1&retain=T`, body = `the payload of your request`

Notice the URI format used to encode MQTT settings.
#### MQTT-PUB syntax
The URI is parsed as follows: `mqtt://{hostname}[:{port}]/{topic-name}[?{settings}]`. The post's body is used as the payload and may be empty, but *note IFTTT may remove newlines or mess with whitespace*. Hence, I suggest using JSON if possible.

Settings must be URI-encoded as usual; the following are valid:
* `qos` = `0` or `1` or `2` (see MQTT specifications for semantics)
* `retain` = `true` or `false` (`1`, `T`, and `true` are all accepted as true)
* `protocol` = `MQTTv31` or `MQTTv311`
