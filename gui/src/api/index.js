import request from '@/utils/request'
//var baseUrl = 'http://8.140.49.13:6789';
var baseUrl = 'http://127.0.0.1:6789';

export function getDataHuiji(params) {
  return request({
    url: baseUrl + '/taocan_analysis',
    method: 'get',
    params: params,
    withCredentials: true
  })
}
export function getDataPeople(params) {
  return request({
    url: baseUrl + '/person_analysis',
    method: 'get',
    params: params,
    withCredentials: true
  })
}
export function changeTaocan(params) {
  return request({
    url: baseUrl + '/switch_taocan',
    method: 'get',
    params: params,
    withCredentials: true
  })
}
export function getCamraList(params) {
  return request({
    url: baseUrl + '/available_cameras',
    method: 'get',
    params: params,
    withCredentials: true
  })
}
export function setCamraList(data) {
  return request({
    url: baseUrl + '/set_camera',
    method: 'post',
    data,
    withCredentials: true
  })
}
export function uploadCamera(data) {
  console.log(data)
  console.log("upload");
  return request({
    url: baseUrl + '/single_upload',
    method: 'post',
    data,
    withCredentials: true
  })
}
export function getConfig(params) {
  return request({
    url: baseUrl + '/get_config',
    method: 'get',
    params: params,
    withCredentials: true
  })
}
export function switchMode(params) {
  return request({
    url: baseUrl + '/switch_mode',
    method: 'get',
    params: params,
    withCredentials: true
  })
}
export function switchType(params) {
  return request({
    url: baseUrl + '/swith_data_type',
    method: 'get',
    params: params,
    withCredentials: true
  })
}
export function modeDatasource(data) {
  return request({
    url: baseUrl + '/mode_datasource',
    method: 'post',
    data,
    withCredentials: true
  })
}