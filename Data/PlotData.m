rawData = AgingTest20160803084204;

%% Get time axis
time = zeros(size(rawData,1),6);
for ii=1:size(rawData,1)
    time(ii,1) = str2num(rawData{ii,1}(1:4));
    time(ii,2) = str2num(rawData{ii,1}(5:6));
    time(ii,3) = str2num(rawData{ii,1}(7:8));
    time(ii,4) = str2num(rawData{ii,1}(10:11));
    time(ii,5) = str2num(rawData{ii,1}(12:13));
    time(ii,6) = str2num(rawData{ii,1}(14:15));
end
%% Convert to seconds from start
timeOrigin = time(1,3)*24*60*60 + time(1,4)*60*60 + time(1,5)*60 + time(1,6);
time(:,7) = (time(:,3)*24*60*60 + time(:,4)*60*60 + time(:,5)*60 + time(:,6)) - timeOrigin;

%% Import other data
thermoTemp = zeros(size(rawData,1),1);
bathTemp = zeros(size(rawData,1),1);
pumpON = zeros(size(rawData,1),1);
for ii=1:size(rawData,1)
thermoTemp(ii) = (rawData{ii,2});
bathTemp(ii) = (rawData{ii,3});
pumpON(ii) = strcmp(rawData{ii,4}, 'Pumping');
end

%% Plots
clf
hold on
plot(time(:,7), thermoTemp, 'o')
plot(time(:,7), bathTemp, 'o')
plot(time(:,7), pumpON*20)
set(gca, 'xtick', 3600*[0:24])
set(gca, 'xtickLabel', num2cell([0:24]))
xlabel('Hours since start')
ylabel('Temperature [C]')
