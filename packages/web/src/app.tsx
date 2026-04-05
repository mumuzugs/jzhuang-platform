import { Component, PropsWithChildren } from 'react';
import { View, Text } from '@tarojs/components';
import './app.scss';

export default class App extends Component<PropsWithChildren<any>> {
  onLaunch() {
    console.log('App launched.');
  }

  render() {
    return (
      <View className="app-container">
        <Text>集装修</Text>
        {this.props.children}
      </View>
    );
  }
}